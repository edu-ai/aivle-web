from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import viewsets
from rest_framework.routers import DefaultRouter

from .models import Submission
from .serializers import SubmissionSerializer

class JobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    permission_classes = (IsAdminUser,)

    def list(self, request):
        if request.method == 'GET':
            submissions = Submission.objects.filter(status=Submission.STATUS_QUEUED).order_by('created_at')
            serializer = self.get_serializer(submissions, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def run(self, request, pk):
        try:
            submission = Submission.objects.get(pk=pk, status=Submission.STATUS_QUEUED)
        except Submission.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        submission.status = Submission.STATUS_RUNNING
        submission.save()
        serializer = self.get_serializer(submission)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def end(self, request, pk):
        UPDATE_ALLOWED = ['verdict', 'point', 'notes', 'status']
        STATUS_ALLOWED = [Submission.STATUS_DONE, Submission.STATUS_ERROR]

        try:
            submission = Submission.objects.get(pk=pk, status=Submission.STATUS_RUNNING)
        except Submission.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        json_data = json.loads(request.body)
        status = json_data.get('status')
        if status and status in STATUS_ALLOWED:
	        for key, value in json_data.items():
	            if key in UPDATE_ALLOWED:
	                setattr(submission, key, value)
	        submission.save()

        serializer = self.get_serializer(submission)
        return Response(serializer.data)

router = DefaultRouter()
router.register(r'jobs', JobViewSet)