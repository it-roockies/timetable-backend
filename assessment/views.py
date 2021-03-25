import csv
from django.http import StreamingHttpResponse
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, ViewSet
from .serializers import QuestionSerializer, AnswerSerializer, ChoiceSerializer
from .models import Question, Answer, Choice


class QuestionViewSet(ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class ChoiceViewSet(ReadOnlyModelViewSet):
    queryset = Choice.objects.all()
    serializer_class = ChoiceSerializer


class AnswerViewSet(ModelViewSet):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answer.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CSVBuffer:
    """An object that implements just the write method of the file-like interface."""
    def write(self, value):
        """Return the string to write."""
        return value


class ExportViewSet(ViewSet):
    """ returns current survey results as a csv file """
    def list(self, request):
        writer = csv.writer(CSVBuffer())
        writer.writerow(['user', 'subject', 'teacher', 'question', 'answer'])

        response = StreamingHttpResponse(
            (writer.writerow([answer.user, answer.subject, answer.teacher, answer.question, answer.answer]) for answer in answers),
            content_type="text/csv"
        )

        response['Content-Disposition'] = 'attachment; filename="answers.csv"'

        return response