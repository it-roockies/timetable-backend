from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from booking.models import Subject, Teacher
import json
def check_json(value):
    print(value)

    try:
        incoming_value = json.loads(value)
        is_list = isinstance(incoming_value, list)
        if not is_list:
            raise ValidationError('You have entered invalid type of data.')
    except:
        raise ValidationError('You have entered invalid type of data.')


class Question(models.Model):
    """question object for users"""
    question_text = models.CharField(max_length=255)
    type_choices = [
        ("choice", "choice"),
        ("text", "text")
    ]
    question_type = models.CharField(max_length=20, choices=type_choices)
    choice = models.ForeignKey("Choice", related_name="choice", on_delete=models.CASCADE, blank=True, null=True)



    def __str__(self):
        return self.question_text


class Choice(models.Model):
    name = models.CharField(max_length=255)
    variant = models.CharField(max_length=255, validators=[check_json])

    def __str__(self):
        return self.name


class Answer(models.Model):
    """answer object"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.answer
