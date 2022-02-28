import logging

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.models import Course, Invitation, Participation
from app.models.course_whitelist import CourseWhitelist
from app.serializers import CourseSerializer, CourseListSerializer, CourseWhitelistSerializer, UserSerializer
from app.utils.permission import has_perm

logger = logging.getLogger("django")


class CoursePermissions(IsAuthenticated):
    def has_permission(self, request, view):
        if not super(CoursePermissions, self).has_permission(request, view):
            return False
        if request.method in ["POST"]:
            return request.user.has_perm("app.add_course")
        return True

    def has_object_permission(self, request, view, obj: Course):
        if request.user.is_superuser:
            return True
        elif request.method in SAFE_METHODS:
            return has_perm(obj, request.user, "course.view")
        elif request.method == "POST":
            return request.user.has_perm("app.add_course")
        elif request.method == "PUT":
            return has_perm(obj, request.user, "course.edit")
        elif request.method == "DELETE":
            return has_perm(obj, request.user, "course.delete")
        return False


class CourseViewSet(ModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [CoursePermissions]

    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = ["participants"]

    def get_serializer_class(self, *args, **kwargs):
        """Instantiate the list of serializers per action from class attribute (must be defined)."""
        kwargs['partial'] = True
        if self.action == "list":
            return CourseListSerializer
        return super(CourseViewSet, self).get_serializer_class()

    def get_queryset(self):
        if self.request.user.has_perm("app.view_invisible_course"):
            return Course.objects.all()
        else:
            return Course.objects.filter(visible=True)

    invitation_token_param = openapi.Parameter('token', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True,
                                               description='invitation token')

    @action(methods=["get"], detail=False)
    @swagger_auto_schema(manual_parameters=[invitation_token_param])
    def join_with_invitation(self, request):
        """
        Join a course with invitation token.
        Course information is inferred from a valid token.
        """
        if "token" not in request.query_params:
            return Response(data={"reason": "no token found in query param"}, status=status.HTTP_400_BAD_REQUEST)
        token = request.query_params["token"]
        try:
            invitation = Invitation.objects.get(token=token)
            if not invitation.is_valid:
                return Response(data={"reason": "invitation expired or invalidated"},
                                status=status.HTTP_400_BAD_REQUEST)
            if Participation.objects.filter(user=request.user, course=invitation.course).exists():
                return Response(data={"reason": "already joined this course"},
                                status=status.HTTP_400_BAD_REQUEST)
            if invitation.course.use_whitelist and \
                    not CourseWhitelist.objects.filter(course=invitation.course, email=request.user.email).exists():
                return Response(data={"reason": "the course has an email whitelist and you are not on the list"},
                                status=status.HTTP_400_BAD_REQUEST)
            p = Participation(user=request.user, course=invitation.course, role=invitation.role)
            p.save()
            return Response(CourseSerializer(invitation.course).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(data={"reason": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["get"], detail=True)
    def enable_whitelist(self, request, pk):
        course = self.get_object()
        if not has_perm(course, request.user, "course.edit_whitelist"):
            return Response(data={"reason": "you do not have edit whitelist access to this course"},
                            status=status.HTTP_401_UNAUTHORIZED)
        if course.use_whitelist:
            return Response(data={"reason": "course already enabled whitelist"},
                            status=status.HTTP_400_BAD_REQUEST)
        course.use_whitelist = True
        course.save()
        whitelist = []
        for user in course.participants.all():
            if user.email:
                w = CourseWhitelist(course=course, email=user.email)
                whitelist.append(w)
                w.save()
        return Response(data=CourseWhitelistSerializer(whitelist, many=True).data, status=status.HTTP_200_OK)

    @action(methods=["get"], detail=True)
    def disable_whitelist(self, request, pk):
        course = self.get_object()
        if not has_perm(course, request.user, "course.edit_whitelist"):
            return Response(data={"reason": "you do not have edit whitelist access to this course"},
                            status=status.HTTP_401_UNAUTHORIZED)
        if not course.use_whitelist:
            return Response(data={"reason": "course did not enable whitelist"},
                            status=status.HTTP_400_BAD_REQUEST)
        course.use_whitelist = False
        course.save()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"])
    def batch_add_whitelist(self, request, pk):
        course = self.get_object()
        if not has_perm(course, request.user, "course.edit_whitelist"):
            return Response(data={"reason": "you do not have edit whitelist access to this course"},
                            status=status.HTTP_401_UNAUTHORIZED)
        email_list = request.data.get("email_list")
        logger.debug(email_list)
        success_list = []
        for email in email_list:
            try:
                cwl = CourseWhitelist(course=course, email=email)
                cwl.save()
                success_list.append(cwl)
            except Exception as e:
                logger.warning(e)
        return Response(data=CourseWhitelistSerializer(success_list, many=True, read_only=True).data,
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"])
    def get_participants(self, request, pk):
        course = self.get_object()
        resp = []
        for participation in Participation.objects.filter(course=course).all():
            resp.append({
                "user": UserSerializer(participation.user).data,
                "role": participation.role
            })
        return Response(data=resp,
                        status=status.HTTP_200_OK)
