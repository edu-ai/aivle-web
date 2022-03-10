from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.viewsets import ModelViewSet

from aiVLE.settings import ROLES_PARTICIPATION_VIEW
from app.models import Participation
from app.serializers import ParticipationSerializer
from app.utils.permission import has_perm


class ParticipationPermissions(IsAuthenticated):
    def has_permission(self, request, view):
        if not super(ParticipationPermissions, self).has_permission(request, view):
            return False
        return request.method != "POST"

    def has_object_permission(self, request, view, obj):
        participation = obj
        if request.user.is_superuser:
            return True
        elif request.method in SAFE_METHODS:
            return has_perm(participation.course, request.user, "participation.view")
        elif request.method == "POST":
            return False  # only superuser is allowed to create new participation directly
        elif request.method == "PUT":
            return has_perm(participation.course, request.user, "participation.edit")
        elif request.method == "DELETE":
            return has_perm(participation.course, request.user, "participation.delete")
        return False


class ParticipationViewSet(ModelViewSet):
    serializer_class = ParticipationSerializer
    permission_classes = [ParticipationPermissions]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["course"]

    def get_queryset(self):
        viewable_courses = []
        for participation in Participation.objects.filter(user=self.request.user.pk, role__in=ROLES_PARTICIPATION_VIEW):
            viewable_courses.append(participation.course)
        return Participation.objects.filter(course__in=viewable_courses)
