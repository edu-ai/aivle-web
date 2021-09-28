from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.models import Course, Invitation, Participation
from app.models.invitation import is_valid_invitation
from app.serializers import CourseSerializer, CourseListSerializer
from app.utils.permission import has_perm


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

    @action(methods=["get"], detail=False)
    def join_with_invitation(self, request):
        if "token" not in request.query_params:
            return Response(data={"reason": "no token found in query param"}, status=status.HTTP_400_BAD_REQUEST)
        token = request.query_params["token"]
        try:
            invitation = Invitation.objects.get(token=token)
            if not is_valid_invitation(invitation):
                return Response(data={"reason": "invitation expired or invalidated"},
                                status=status.HTTP_400_BAD_REQUEST)
            if Participation.objects.filter(user=request.user, course=invitation.course).exists():
                return Response(data={"reason": "already joined this course"},
                                status=status.HTTP_400_BAD_REQUEST)
            p = Participation(user=request.user, course=invitation.course, role=invitation.role)
            p.save()
            return Response(CourseSerializer(invitation.course).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(e)
            return Response(data={"reason": "invalid token"}, status=status.HTTP_400_BAD_REQUEST)
