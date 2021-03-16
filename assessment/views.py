from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet

from .serializers import QuestionSerializer, AnswerSerializer
from .models import Question, Answer


class QuestionViewSet(ReadOnlyModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer


class AnswerViewSet(ModelViewSet):
    serializer_class = AnswerSerializer

    def get_queryset(self):
        return Answer.objects.filter(user=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)