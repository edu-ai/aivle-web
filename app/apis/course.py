from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from app.models import Course
from app.serializers import CourseSerializer, CourseListSerializer
from app.utils.permission import can


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
        if request.method in SAFE_METHODS:
            return can(obj, request.user, "course.view")
        elif request.method == "POST":
            return request.user.has_perm("app.add_course")
        elif request.method == "PUT":
            return can(obj, request.user, "course.edit")
        elif request.method == "DELETE":
            return can(obj, request.user, "course.delete")


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
