from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from aiVLE.settings import ROLES_INVITATION_VIEW
from app.models import Invitation, Course, Participation
from app.serializers import InvitationSerializer
from app.utils.permission import has_perm


class InvitationPermissions(IsAuthenticated):
    def has_permission(self, request, view):
        if not super(InvitationPermissions, self).has_permission(request, view):
            return False
        if request.method == "POST":
            data = request.data
            if "course" not in request.data:
                return True  # hack
            course = Course.objects.get(pk=int(data["course"][0]))
            return has_perm(course, request.user, "invitation.add")
        return True

    def has_object_permission(self, request, view, obj: Invitation):
        if request.user.is_superuser:
            return True
        elif request.method in SAFE_METHODS:
            return has_perm(obj.course, request.user, "invitation.view")
        elif request.method == "POST":
            return has_perm(obj.course, request.user, "invitation.add")
        elif request.method == "PUT":
            return has_perm(obj.course, request.user, "invitation.edit")
        elif request.method == "DELETE":
            return has_perm(obj.course, request.user, "invitation.delete")
        return False


class InvitationViewSet(ModelViewSet):
    serializer_class = InvitationSerializer
    permission_classes = [InvitationPermissions]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "valid"]
    ordering_fields = ["valid_from", "valid_to"]

    def get_queryset(self):
        viewable_courses = []
        for participation in Participation.objects.filter(user=self.request.user.pk, role__in=ROLES_INVITATION_VIEW):
            viewable_courses.append(participation.course)
        return Invitation.objects.filter(course__in=viewable_courses)
