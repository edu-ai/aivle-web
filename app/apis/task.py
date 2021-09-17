from itertools import groupby

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from app.funcs import can
from app.models import Task
from app.serializers import TaskSerializer, SimilaritySubmissionSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAdminUser,)

    @action(detail=True, methods=['get'])
    def submissions_by_user(self, request, pk):
        if request.method == 'GET':
            task = Task.objects.get(pk=pk)
            submissions = task.submissions.all()
            key = lambda x: x.user
            grouped_submissions = groupby(sorted(submissions, key=lambda x: x.user.pk), key=key)
            result = {}
            for user, submissions in grouped_submissions:
                if can(task.course, user, 'task.edit') or not user.is_active:
                    continue
                serializer = SimilaritySubmissionSerializer(submissions, many=True, context={'request': request})
                result[user.pk] = serializer.data
            return Response(result)
