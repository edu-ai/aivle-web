from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from app.models import Invitation, Course
from app.serializers import InvitationSerializer
from app.utils.permission import can
from aiVLE.settings import ROLES_INVITATION_VIEW


class InvitationPermissions(IsAuthenticated):
    def has_permission(self, request, view):
        if not super(InvitationPermissions, self).has_permission(request, view):
            return False
        if request.method == "POST":
            data = request.data
            if "course" not in request.data:
                return True  # hack
            course = Course.objects.get(pk=int(data["course"][0]))
            return can(course, request.user, "invitation.add")
        return True

    def has_object_permission(self, request, view, obj: Invitation):
        if request.user.is_superuser:
            return True
        elif request.method in SAFE_METHODS:
            return can(obj.course, request.user, "invitation.view")
        elif request.method == "POST":
            return can(obj.course, request.user, "invitation.add")
        elif request.method == "PUT":
            return can(obj.course, request.user, "invitation.edit")
        elif request.method == "DELETE":
            return can(obj.course, request.user, "invitation.delete")


class InvitationViewSet(ModelViewSet):
    serializer_class = InvitationSerializer
    permission_classes = [InvitationPermissions]

    def get_queryset(self):
        return Invitation.objects.filter(course__participants__username__contains=self.request.user.username,
                                         course__participation__role__in=ROLES_INVITATION_VIEW)
