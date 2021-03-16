from datetime import date, timedelta
import xml.etree.ElementTree as ET
from . import serializers
from . import models
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework import generics
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework.views import APIView

class BookingViewSet(ReadOnlyModelViewSet):
    """Interacts with booking"""
    queryset = models.Booking.objects.all()
    serializer_class = serializers.BookingSerializer

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


class TimeTableViewSet(ViewSet):
    """ Returns table date for current week """
    def list(self, request):
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

        bookings = models.Booking.objects.filter(date__range=[start_date, end_date]).order_by('date')

        



    """Interacts with incoming 'xml'file """
    def create(self, request):
        """takes file and stores information into database"""
        file = request.FILES['file']
        tree = ET.parse(file)
        root = tree.getroot()

        # Import Subjects
        for child in root.iter('subject'):
            models.Subject.objects.get_or_create(
                subject_id=child.attrib['id'],
                defaults={
                    'name': child.attrib['name'],
                    'short': child.attrib['short'],
                }
            )

        # Import Teachers
        for child in root.iter('teacher'):
            models.Teacher.objects.get_or_create(
                teacher_id=child.attrib['id'],
                defaults={
                    'firstname': child.attrib['firstname'],
                    'lastname': child.attrib['lastname'],
                    'short': child.attrib['short'],
                    # for booking -> 'module': models.Module.objects.get(subject_id=child.attrib['subject'])
                }
            )
        # Import days
        for child in root.iter('daysdef'):
            models.Day.objects.get_or_create(
                day_id=child.attrib['id'],
                defaults={
                    'day': child.attrib['days']
                }
            )
        # Import Weeks
        for child in root.iter('weeksdef'):
            models.Week.objects.get_or_create(
                week_id=child.attrib['id'],
                defaults={
                    'week': child.attrib['weeks']
                }
            )

        # Import Terms
        for child in root.iter('termsdef'):
            models.Term.objects.get_or_create(
                term_id=child.attrib['id'],
                defaults={
                    'term': child.attrib['terms']
                }
            )

        # import Groups
        for child in root.iter('class'):
            models.Group.objects.get_or_create(
                group_id=child.attrib['id'],
                defaults={
                    'name': child.attrib['name'],
                }
            )
        # import classroom
        for child in root.iter('classroom'):
            models.Classroom.objects.get_or_create(
                classroom_id=child.attrib['id'],
                defaults={
                    'name': child.attrib['name'],
                }
            )

        lessons = {}
        for child in root.iter('lesson'):
            lessons[child.attrib['id']] = {
                'teacher_id': child.attrib['teacherids'],
                'subject_id': child.attrib['subjectid'],
                'group_id': child.attrib['classids'].split(',')[0]
            }

        for child in root.iter('card'):
            booking_date = get_date_for_day(child.attrib['days'])
            period = child.attrib['period']
            group_id = lessons[child.attrib['lessonid']]['group_id']
            classroom_id = child.attrib['classroomids'].split(',')[0]
            teacher_id = lessons[child.attrib['lessonid']]['teacher_id']
            subject_id = lessons[child.attrib['lessonid']]['subject_id']

            classroom_object = models.Classroom.objects.get(classroom_id=classroom_id)
            group_object = models.Group.objects.get(group_id=group_id)
            teacher_object = models.Teacher.objects.get(teacher_id=teacher_id)
            subject_object = models.Subject.objects.get(subject_id=subject_id)

            models.Booking.objects.get_or_create(
                date=booking_date,
                period=period,
                group=group_object,
                classroom=classroom_object,
                teacher=teacher_object,
                subject=subject_object
            )

        msg = {'success': 'data is successfully stored'}
        return Response(msg, status=status.HTTP_201_CREATED)


DAYS_MAP = {
    '100000': 0,
    '010000': 1,
    '001000': 2,
    '000100': 3,
    '000010': 4,
    '000001': 5,
}


def get_date_for_day(day):
    today = date.today()
    start = today - timedelta(days=today.weekday())
    result = start + timedelta(days=DAYS_MAP[day])
    return result
