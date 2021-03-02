from django.shortcuts import render
from . import serializers
from . import models
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.

class CreateUserView(APIView):
    """Handles user object in the system"""
    def post(self, request):
        serializer = serializers.UserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            msg = {"success": "You have successfully been registered"}
            return Response(msg, status=status.HTTP_201_CREATED)


class BookingApiView(APIView):
    """Interacts with booking"""


    def get(self, request):
        """returns all booking details """
        bookings = models.Booking.objects.all()
        serializer = serializers.BookingSerializer(bookings, many=True)
        print(serializer.data)
        print(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

class TutorApiView(APIView):
    """Interacts with tutors"""
    def get(self, request):
        """returns all existing tutors in our database"""
        tutors = models.Tutor.objects.all()
        serializer = serializers.TutorSerializer(tutors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class GroupApiView(APIView):
    """Interacts with groups"""
    def get(self, request):
        """returns all existing groups in our database"""
        groups = models.Group.objects.all()
        serializer = serializers.GroupSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RoomApiView(APIView):
    """Interacts with rooms"""
    def get(self, request):
        """returns all existing room in our database"""
        rooms = models.Room.objects.all()
        serializer = serializers.RoomSerializer(rooms, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ModuleApiView(APIView):
    """Interacts with tutors"""
    def get(self, request):
        """returns all existing tutors in our database"""
        modules = models.Module.objects.all()
        serializer = serializers.ModuleSerializer(modules, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
