from django.urls import path
from .views import AnswerApiView, QuestionApiView

urlpatterns = [
    path('question/', QuestionApiView.as_view(), name='question'),
    path('answer/', AnswerApiView.as_view(), name='answer')
]
