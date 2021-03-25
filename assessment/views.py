from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
import csv
from django.http import HttpResponse
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


def csv_file(request):
    """returns current survey results as a csv file"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="answers.csv"'

    writer = csv.writer(response)
    writer.writerow(['user', 'subject', 'teacher', 'question', 'answer'])
    answers = Answer.objects.all()
    for answer in answers:
        writer.writerow([answer.user, answer.subject, answer.teacher, answer.question, answer.answer])

    return response
