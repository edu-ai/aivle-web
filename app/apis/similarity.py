import json

from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_404_NOT_FOUND

from app.models import Similarity, Task, Submission
from app.serializers import SimilaritySerializer


class SimilarityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Similarity.objects.all()
    serializer_class = SimilaritySerializer
    permission_classes = (IsAdminUser,)

    @action(detail=False, methods=['post'])
    def set(self, request):
        UPDATE_ALLOWED = ['score', 'diff']

        json_data = json.loads(request.body)
        try:
            user = User.objects.get(pk=json_data.get('user_id'))
            task = Task.objects.get(pk=int(json_data.get('task_id')))
            submission = Submission.objects.get(pk=json_data.get('submission_id'))
            related = Submission.objects.get(pk=json_data.get('related_id'))
            similarity = Similarity.objects.get(user=user, task=task)
        except (User.DoesNotExist, Task.DoesNotExist):
            return Response(status=HTTP_404_NOT_FOUND)
        except Similarity.DoesNotExist:
            similarity = Similarity(user=user, task=task)

        similarity.submission = submission
        similarity.related = related

        for key in UPDATE_ALLOWED:
            setattr(similarity, key, json_data[key])

        similarity.save()

        serializer = self.get_serializer(similarity)
        return Response(serializer.data)