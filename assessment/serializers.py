from rest_framework import serializers
from .models import Question, Answer, Choice

class QuestionSerializer(serializers.ModelSerializer):
    # choice = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'question_text', 'choice']


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ['id', 'answer', 'teacher', 'subject', 'question']

class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Choice
        fields = ["id", "name", "variant"]
