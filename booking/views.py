import xml.etree.ElementTree as ET
from . import serializers
from . import models
from rest_framework import generics
from rest_framework import status
from rest_framework.viewsets import ReadOnlyModelViewSet
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
            serializer.save()
            msg = {"success": "You have successfully been registered"}
            return Response(msg, status=status.HTTP_201_CREATED)


class BookingApiViewSet(ReadOnlyModelViewSet):
    """Interacts with booking"""
    queryset = models.Booking.objects.all()
    serializer_class = serializers.BookingSerializer


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

class TimeTableDataApiView(APIView):
    """Interacts with incoming 'xml'file """
    def post(self, request):
        """takes file and stores information into database"""
        file = request.FILES['file']
        tree = ET.parse(file)
        root = tree.getroot()

        # Import Subjects
        for child in root.iter('subject'):
            models.Module.objects.get_or_create(
                subject_id=child.attrib['id'],
                defaults={
                    'name': child.attrib['name'],
                    'short_name': child.attrib['short'],
                }
            )

        # Import Teachers
        for child in root.iter('teacher'):
            models.Tutor.objects.get_or_create(
                teacher_id=child.attrib['id'],
                defaults={
                    'first_name': child.attrib['firstname'],
                    'last_name': child.attrib['lastname'],
                    'short_name': child.attrib['short'],
                    # for booking -> 'module': models.Module.objects.get(subject_id=child.attrib['subject'])
                }
            )

        msg = {'success': 'data is successfully stored'}
        return Response(msg, status=status.HTTP_201_CREATED)

