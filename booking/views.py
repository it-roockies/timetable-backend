
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import FileUploadParser
from rest_framework.permissions import BasePermission, IsAdminUser, AllowAny
from authentication.authentication import TelegramBotAuthentication
from .import_students import import_students
from .import_timetable import import_timetable
from . import serializers
from . import models
from . import filters

class BookingViewSet(ReadOnlyModelViewSet):
    """Interacts with booking"""
    permission_classes = (AllowAny, )
    queryset = models.Booking.objects.all()
    serializer_class = serializers.BookingSerializer
    filter_backends = (filters.BookingWeekFilter, )


class TeacherViewSet(ReadOnlyModelViewSet):
    """Interacts with teachers"""
    permission_classes = (AllowAny, )
    queryset = models.Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer


class GroupViewSet(ReadOnlyModelViewSet):
    """Interacts with groups"""
    permission_classes = (AllowAny, )
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer


class ClassroomViewSet(ReadOnlyModelViewSet):
    """Interacts with rooms"""
    permission_classes = (AllowAny, )
    queryset = models.Classroom.objects.all()
    serializer_class = serializers.ClassroomSerializer


class SubjectViewSet(ReadOnlyModelViewSet):
    """Interacts with rooms"""
    permission_classes = (AllowAny, )
    queryset = models.Subject.objects.all()
    serializer_class = serializers.SubjectSerializer


class MessageViewSet(ReadOnlyModelViewSet):
    """returns all available messages """
    authentication_classes = [TelegramBotAuthentication]
    queryset = models.Message.objects.all()
    serializer_class = serializers.MessageSerializer

class TimeTablePermission(BasePermission):
    """
    Get Timetable for anonymous, Import Timatable for admins.
    """

    def has_permission(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return bool(request.user and request.user.is_staff)


period_in_minutes = {0: 0, 1: 600, 2: 680, 3: 780, 4: 860, 5: 940, 6: 1020}
class GroupLessonViewSet(ViewSet):
    """returns lessons to the user for given date"""
    # authentication_classes = []
    # permission_classes = []
    def list(self, request):
        date = request.data.get('date')  # date of the lesson for a particular group
        group = request.data.get('group')  # group
        minutes = request.data.get('minutes')
        bookings = models.Booking.objects.filter(date=date)  # filtering bookings through data
        now_lesson = {"message": 'You are not supposed to be in any lesson right now'}
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
                teachers = booking.lesson.teachers.all()
                teacher = ''
                if len(teachers) != 1:
                    for t in teachers:
                        teacher += t.short
                else:
                    teacher = teachers[0].short
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
                if period_in_minutes[int(card.period)-1] <= int(minutes) <= period_in_minutes[int(card.period)]:
                    today_serializer = serializers.CardSerializer(card)
                    now_lesson = today_serializer.data
        if len(cards) == 0:
            msg = {'message': "Today you have no classes"}
            return Response(msg, status=status.HTTP_200_OK)
        serializer = serializers.CardSerializer(cards, many=True)

        ready_data = {
            'today_lessons': serializer.data,
            'now_lesson': now_lesson
        }
        return Response(ready_data, status=status.HTTP_200_OK)


class TimeTableViewSet(ViewSet):
    permission_classes = (TimeTablePermission, )

    """ Returns table date for current week """
    def list(self, request):
        filter_kwars = {}
        if 'group' in request.query_params:
            filter_kwars['lesson__groups__id__in'] = request.query_params.getlist('group')

        if 'teacher' in request.query_params:
            filter_kwars['lesson__teachers__id__in'] = request.query_params.getlist('teacher')

        if 'classroom' in request.query_params:
            filter_kwars['classroom_id__in'] = request.query_params.getlist('classroom')

        if 'date' in request.query_params:
            filter_kwars['date'] = request.query_params.get('date')

        elif 'week' in request.query_params:
            week = request.query_params.get('week')
            if week == 'current':
                tomorrow = date.today() + timedelta(days=1)
                start_date = tomorrow - timedelta(days=tomorrow.weekday())
                end_date = start_date + timedelta(days=6)
                filter_kwars['date__range'] = [start_date, end_date]

        if 'date' not in filter_kwars and 'date__range' not in filter_kwars:
            today = date.today() # get today's date
            if today.weekday() == 6:
                filter_kwars['date'] = today + timedelta(days=1)
            else:
                filter_kwars['date'] = today

        bookings = [{
            "id": booking.id,
            "lesson_id": booking.lesson.id,
            "date": booking.date,
            "period": booking.period,
            "subject": {
                "id": booking.lesson.subject.id,
                "name": booking.lesson.subject.short,
            },
            "teachers": [{
                "id": teacher.id,
                "name": teacher.short,
            } for teacher in booking.lesson.teachers.all()],
            "groups": [{
                "id": group.id,
                "name": group.name,
            } for group in booking.lesson.groups.all()],
            "classroom": {
                "id": booking.classroom.id,
                "name": booking.classroom.name,
            } if booking.classroom else None,
        } for booking in models.Booking.objects.filter(**filter_kwars).order_by('date')]

        return Response(bookings, status=status.HTTP_200_OK)

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
