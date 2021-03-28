
from datetime import date

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import BasePermission, IsAdminUser

from .import_students import import_students
from .import_timetable import import_timetable
from . import serializers
from . import models


class BookingViewSet(ReadOnlyModelViewSet):
    """Interacts with booking"""
    queryset = models.Booking.objects.all()
    serializer_class = serializers.BookingSerializer

class TeacherViewSet(ReadOnlyModelViewSet):
    """Interacts with teachers"""
    queryset = models.Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer


class GroupViewSet(ReadOnlyModelViewSet):
    """Interacts with groups"""
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer


class ClassroomViewSet(ReadOnlyModelViewSet):
    """Interacts with rooms"""
    queryset = models.Classroom.objects.all()
    serializer_class = serializers.ClassroomSerializer


class SubjectViewSet(ReadOnlyModelViewSet):
    """Interacts with rooms"""
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer



class TimeTablePermission(BasePermission):
    """
    Get Timetable for anonymous, Import Timatable for admins.
    """

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return bool(request.user and request.user.is_staff)

class GroupLessonViewSet(ViewSet):
    """returns lessons to the user for given date"""
    # authentication_classes = []
    # permission_classes = []
    def list(self, request):
        date = request.data.get('date')  # date of the lesson for a particular group
        group = request.data.get('group')  # group
        bookings = models.Booking.objects.filter(date=date)  # filtering bookings through data
        cards = []
        for booking in bookings:  # given data's bookings
            try:
                groupid = models.Group.objects.get(name=group).id  # group id for given group name
                groupids = [group.id for group in booking.lesson.groups.all()]  # group ids for a particular lesson.
                # some lesson has more than one group
            except:
                continue
            if groupid in groupids:  # checking whether given group has lesson in this booking
                date = booking.date
                period = booking.period
                subject = booking.lesson.subject.short
                teacher = booking.lesson.teacher.short
                try:
                    classroom = booking.classroom.name
                except:
                    classroom = None
                card = models.Card(period=period,
                                   date=date,
                                   classroom=classroom,
                                   group=group,
                                   teacher=teacher,
                                   subject=subject
                                   )
                cards.append(card)
        if len(cards) == 0:
            msg = {'message': "Today you have no classess"}
            return Response(msg, status=status.HTTP_200_OK)

        serializer = serializers.CardSerializer(cards, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TimeTableViewSet(ViewSet):
    permission_classes = (TimeTablePermission, )

    """ Returns table date for current week """
    def list(self, request):
        today = date.today()  # get today's date
        bookings = models.Booking.objects.filter(date=today)  # getting all bookings for today

        cards = []
        for booking in bookings:
            for group in booking.lesson.groups.all():
                cards.append({
                    "booking_id": booking.id,
                    "lesson_id": booking.lesson.id,
                    "date": booking.date,
                    "period": booking.period,
                    "subject": {
                        "id": booking.lesson.subject.id,
                        "name": booking.lesson.subject.short,
                    },
                    "teacher": {
                        "id": booking.lesson.teacher.id,
                        "name": booking.lesson.teacher.short,
                    },
                    "group": {
                        "id": group.id,
                        "name": group.name,
                    },
                    "classroom": {
                        "id": booking.classroom.id,
                        "name": booking.classroom.name,
                    } if booking.classroom else None,
                })

        groups = models.Group.objects.all()
        serializer = serializers.GroupSerializer(groups, many=True)

        return Response({
            "bookings": cards,
            "groups": serializer.data,
        }, status=status.HTTP_200_OK)

    """Interacts with incoming 'xml'file """
    def create(self, request):
        week = request.data.get('week')
        _file = request.data.get('file')

        import_timetable(week, _file)

        msg = {'message': 'all bookings are successfully stored'}
        return Response(msg, status=status.HTTP_201_CREATED)


class UserViewSet(ViewSet):
    permission_classes = (IsAdminUser, )

    """manages users"""
    def list(self, request):
        """returns all students in our database"""
        users = get_user_model().objects.all()
        serializer = serializers.UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def create(self, request):
        """handles incoming student list"""
        csv_file = request.data.get('file')

        import_students(csv_file)

        msg = {"message": "student list have successfully been stored"}
        return Response(msg, status=status.HTTP_201_CREATED)
