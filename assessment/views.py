import csv
from asgiref.sync import sync_to_async
from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, ViewSet
from authentication.authentication import TimeLimitedQueryParamTokenAuthentication
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


def get_headers():
    return ['user', 'subject', 'teacher', 'question', 'answer']


def get_data(answer):
    return {
        'user': answer.user,
        'subject': answer.subject,
        'teacher': answer.teacher,
        'question': answer.question,
        'answer': answer.answer
    }


class Echo(object):
    def write(self, value):
        return value


def iter_items(items, pseudo_buffer):
    writer = csv.DictWriter(pseudo_buffer, fieldnames=get_headers())
    yield pseudo_buffer.write("user,subject,teacher,question,answer\n")

    for item in items:
        yield writer.writerow(get_data(item))


class ExportViewSet(ViewSet):
    authentication_classes = [TimeLimitedQueryParamTokenAuthentication]
    
    """ returns current survey results as a csv file """
    def list(self, request):
        queryset = Answer.objects.all()
        response = StreamingHttpResponse(
            streaming_content=(iter_items(queryset, Echo())),
            content_type='text/csv',
        )

        response['Content-Disposition'] = 'attachment; filename="answers.csv"'

        return response