from django.db import models
from django.conf import settings
# Create your models here.

class Question(models.Model):
    """question object for users"""
    question_text = models.CharField(max_length=256)

    def __str__(self):
        return self.question_text

class Answer(models.Model):
    """answer object"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=256)
    teacher = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)

    def __str__(self):
        return self.answer
