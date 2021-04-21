from datetime import datetime, date, timedelta

from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition
from django_filters.rest_framework import DjangoFilterBackend

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
from .import_teacherlesson import import_teacher_lesson
from . import serializers
from . import models
from . import filters
from django.db.models import Max


def last_modified(request, *args, **kwargs):
    return cache.get_or_set("last_modified", datetime.utcnow())


class CachedReadOnlyModelViewSet(ReadOnlyModelViewSet):
    @method_decorator(condition(last_modified_func=last_modified))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class BookingViewSet(CachedReadOnlyModelViewSet):
    """Interacts with booking"""

    permission_classes = (AllowAny,)
    queryset = models.Booking.objects.all()
    serializer_class = serializers.BookingSerializer
    filter_backends = (filters.BookingWeekFilter,)


class TeacherViewSet(CachedReadOnlyModelViewSet):
    """Interacts with teachers"""

    permission_classes = (AllowAny,)
    queryset = models.Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer


class GroupViewSet(CachedReadOnlyModelViewSet):
    """Interacts with groups"""

    permission_classes = (AllowAny,)
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer


class ClassroomViewSet(CachedReadOnlyModelViewSet):
    """Interacts with rooms"""

    permission_classes = (AllowAny,)
    queryset = models.Classroom.objects.all()
    serializer_class = serializers.ClassroomSerializer


class SubjectViewSet(CachedReadOnlyModelViewSet):
    """Interacts with rooms"""

    permission_classes = (AllowAny,)
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
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(request.user and request.user.is_staff)


period_in_minutes = {0: 0, 1: 600, 2: 680, 3: 780, 4: 860, 5: 940, 6: 1020, 7: 1100}
period_in_time = {
    1: "09:00-10:00",
    2: "10:20-11:20",
    3: "12:00-13:00",
    4: "13:20-14:20",
    5: "14:40-15:40",
    6: "16:00-17:00",
    7: "17:20-18:20",
}


class GroupLessonViewSet(ViewSet):
    """returns lessons to the user for given date"""

    # authentication_classes = []
    # permission_classes = []
    def list(self, request):
        date = request.data.get("date")  # date of the lesson for a particular group
        group = request.data.get("group")  # group
        minutes = request.data.get("minutes")
        bookings = models.Booking.objects.filter(date=date)  # filtering bookings through data
        now_lesson = {"message": "You are not supposed to be in any lesson right now"}
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
                teacher = ""
                if len(teachers) != 1:
                    for t in teachers:
                        teacher += t.short
                else:
                    teacher = teachers[0].short
                try:
                    classroom = booking.classroom.name
                except:
                    classroom = None
                card = dict(
                    period=period,
                    date=date,
                    classroom=classroom,
                    group=group,
                    teacher=teacher,
                    subject=subject,
                    time=period_in_time[int(period)],  # get time for lesson
                )
                cards.append(card)
                if period_in_minutes[int(period) - 1] <= int(minutes) <= period_in_minutes[int(period)]:
                    now_lesson = card

        if len(cards) == 0:
            msg = {"message": "Today you have no classes"}
            return Response(msg, status=status.HTTP_200_OK)

        # sorting lessons by period
        cards = sorted(cards, key=lambda card: card["period"])
        return Response({"today_lessons": cards, "now_lesson": now_lesson}, status=status.HTTP_200_OK)


class NotifyUserViewSet(ViewSet):
    """helps to notify student about lesson"""

    authentication_classes = [TelegramBotAuthentication]

    def list(self, request):
        period = request.data.get("period")
        today = request.data.get("date")
        bookings = models.Booking.objects.filter(date=today, period=period)
        data = []
        for booking in bookings:  # all lessons for a given period
            ready_dic = {}
            ready_dic["teachers"] = [teacher.short for teacher in booking.lesson.teachers.all()]  # getting teacher
            ready_dic["subject"] = booking.lesson.subject.short
            ready_dic["telegram_ids"] = [
                user.telegram_id
                for user in models.User.objects.filter(group__in=booking.lesson.groups.all(), telegram_id__isnull=False)
            ]
            data.append(ready_dic)
        return Response(data, status=status.HTTP_200_OK)


class TimeTableViewSet(ViewSet):
    permission_classes = (TimeTablePermission,)

    """ Returns table date for current week """

    def list(self, request):
        filter_kwars = {}
        if "id" in request.query_params:
            filter_kwars["id__in"] = request.query_params.getlist("id")
        if "group" in request.query_params:
            filter_kwars["lesson__groups__id__in"] = request.query_params.getlist("group")

        if "teacher" in request.query_params:
            filter_kwars["lesson__teachers__id__in"] = request.query_params.getlist("teacher")

        if "classroom" in request.query_params:
            filter_kwars["classroom_id__in"] = request.query_params.getlist("classroom")

        if "date" in request.query_params:
            filter_kwars["date"] = request.query_params.get("date")

        elif "week" in request.query_params:
            week = request.query_params.get("week")
            if week == "current":
                tomorrow = date.today() + timedelta(days=1)
                start_date = tomorrow - timedelta(days=tomorrow.weekday())
            else:
                start_date = datetime.strptime(f"{week}-1", "%Y-W%W-%w").date()
            end_date = start_date + timedelta(days=6)
            filter_kwars["date__range"] = [start_date, end_date]

        if "date" not in filter_kwars and "date__range" not in filter_kwars and "id__in" not in filter_kwars:
            today = date.today()  # get today's date
            if today.weekday() == 6:
                filter_kwars["date"] = today + timedelta(days=1)
            else:
                filter_kwars["date"] = today

        bookings = [
            {
                "id": booking.id,
                "lesson_id": booking.lesson.id,
                "date": booking.date,
                "period": booking.period,
                "subject": {
                    "id": booking.lesson.subject.id,
                    "name": booking.lesson.subject.short,
                },
                "teachers": [
                    {
                        "id": teacher.id,
                        "name": teacher.short,
                    }
                    for teacher in booking.lesson.teachers.all()
                ],
                "groups": [
                    {
                        "id": group.id,
                        "name": group.name,
                    }
                    for group in booking.lesson.groups.all()
                ],
                "classroom": {
                    "id": booking.classroom.id,
                    "name": booking.classroom.name,
                }
                if booking.classroom
                else None,
            }
            for booking in models.Booking.objects.filter(**filter_kwars).order_by("date")
        ]

        return Response(bookings, status=status.HTTP_200_OK)

    """Interacts with incoming 'xml'file """

    def create(self, request):
        week = request.data.get("week")
        _file = request.data.get("file")

        import_timetable(week, _file)
        cache.delete("last_modified")

        msg = {"message": "all bookings are successfully stored"}
        return Response(msg, status=status.HTTP_201_CREATED)


class UserViewSet(ViewSet):
    permission_classes = (IsAdminUser,)

    """manages users"""

    def list(self, request):
        """returns all students in our database"""
        users = get_user_model().objects.all()
        serializer = serializers.UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """handles incoming student list"""
        csv_file = request.data.get("file")

        import_students(csv_file)

        msg = {"message": "student list have successfully been stored"}
        return Response(msg, status=status.HTTP_201_CREATED)


class TeacherSubjectViewSet(ViewSet):
    """importing teachers"""

    def create(self, request):
        csv_file = request.data.get("file")
        import_teacher_lesson(csv_file)
        return Response(status=status.HTTP_200_OK)


class LevelSubjectViewSet(ViewSet):
    def list(self, request):
        level = request.data.get("level")
        term = request.data.get("term")
        objects = models.TeacherSubject.objects.filter(level=level, term=term)
        subjects = []
        for obj in objects:
            if obj.subject.name not in subjects:
                subjects.append(obj.subject.name)
        data = dict(subjects=subjects)
        return Response(data, status=status.HTTP_200_OK)


class LevelTeacherViewSet(ViewSet):
    def list(self, request):
        subject = request.data.get("subject")
        objects = models.TeacherSubject.objects.filter(subject__name=subject)
        teachers = []
        for obj in objects:
            if obj.teacher.firstname + " " + obj.teacher.lastname not in teachers:
                teachers.append(obj.teacher.firstname + " " + obj.teacher.lastname)
        data = dict(teachers=teachers)
        return Response(data, status=status.HTTP_200_OK)


class AvailableRoomViewSet(ViewSet):
    def list(self, request):
        """returns all available rooms for today"""
        # start_date = date.today()
        # end_date = start_date + timedelta(5-start_date.weekday())
        day = request.data.get("date")
        # list of rooms which key is classroom and period__max and value is id and actual period
        rooms = list(models.Booking.objects.filter(date=day).values("classroom", "date").annotate(Max("period")))
        # filter available rooms
        available_rooms = []
        for room in rooms:
            if int(room["period__max"]) < 6:
                classroom = models.Classroom.objects.get(id=room["classroom"]).name
                if classroom[:1].isnumeric() or classroom[:3] == "LAB":
                    available_rooms.append(
                        dict(
                            classroom=classroom,
                            starting_time=period_in_time[int(room["period__max"]) + 1][:5],
                            date=room["date"],
                        )
                    )
        return Response(available_rooms, status=status.HTTP_200_OK)


class EventViewSet(ViewSet):
    """Interacts with event object"""

    def create(self, request):
        """Creates and saves a new event"""
        serializer = serializers.EventSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
