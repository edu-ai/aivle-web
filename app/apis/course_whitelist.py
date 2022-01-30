from rest_framework.permissions import IsAuthenticated, SAFE_METHODS

from rest_framework.viewsets import ModelViewSet
from app.utils.permission import has_perm
from app.models import CourseWhitelist
from app.serializers import CourseWhitelistSerializer
from aiVLE.settings import ROLES_COURSE_VIEW_WHITELIST


class CourseWhitelistPermissions(IsAuthenticated):
    def has_object_permission(self, request, view, obj: CourseWhitelist):
        if request.user.is_superuser:
            return True
        elif request.method in SAFE_METHODS:
            return has_perm(obj.course, request.user, "course.view_whitelist")
        else:
            return has_perm(obj.course, request.user, "course.edit_whitelist")


class CourseWhitelistViewset(ModelViewSet):
    serializer_class = CourseWhitelistSerializer
    permission_classes = [CourseWhitelistPermissions]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return CourseWhitelist.objects.all()
        return CourseWhitelist.objects.filter(course__participants__username__exact=self.request.user.username,
                                              course__participation__role__in=ROLES_COURSE_VIEW_WHITELIST)
