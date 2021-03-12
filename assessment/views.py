from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import QuestionSerializer, AnswerSerializer
from .models import Question, Answer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.response import Response
# Create your views here.


class QuestionApiView(APIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """returns all questions in the system"""
        questions = Question.objects.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        """lets an authenticated user to create a new question"""
        serializer = QuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

class AnswerApiView(APIView):

    def post(self, request):
        serializer = AnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer.save(user=request.user)
            msg = {'message': 'thank you for your time and effort.'}
            return Response(msg, status=status.HTTP_201_CREATED)
