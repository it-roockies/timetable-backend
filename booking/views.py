from datetime import date, timedelta
import xml.etree.ElementTree as ET
from . import serializers
from . import models
import csv
from io import StringIO
from django.contrib.auth import get_user_model
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


def get_date_for_day(day):
    """returns date according to week number. 0 is monday"""
    today = date.today()  # getting today's date
    start = today - timedelta(days=today.weekday())  # starting of week's date
    result = start + timedelta(days=DAYS_MAP[day])
    return result

class TimeTableViewSet(ViewSet):
    """ Returns table date for current week """

    def list(self, request):
        from datetime import date
        today = date.today()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)

        bookings = models.Booking.objects.filter(date__range=[start_date, end_date]).order_by('date')
        cards = []
        for booking in bookings:
            date = booking.date
            period = booking.period
            subject = booking.lesson.subject.short
            teacher = booking.lesson.teacher.short
            groups = booking.lesson.groups.all()  # getting all groups that related to one lesson
            group = [group.name for group in groups]
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
        serializer = serializers.CardSerializer(cards, many=True)
        # serializer = serializers.BookingSerializer(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



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
        # import lesson
        for child in root.iter('lesson'):
            lesson_id = child.attrib['id']
            subject_id = child.attrib['subjectid']
            teacher_id = child.attrib['teacherids']
            group_ids = child.attrib['classids'].split(',')
            subject_object = models.Subject.objects.get(subject_id=subject_id)
            teacher_object = models.Teacher.objects.get(teacher_id=teacher_id)
            lesson, _ = models.Lesson.objects.get_or_create(
                lesson_id=lesson_id,
                defaults={
                    'subject': subject_object,
                    'teacher': teacher_object
                }
            )
            groups = models.Group.objects.filter(group_id__in=group_ids)
            lesson.groups.set(groups)

        # import Booking
        for child in root.iter('card'):
            booking_date = get_date_for_day(child.attrib['days'])
            period = child.attrib['period']
            classroom_id = child.attrib['classroomids']
            lesson_id = child.attrib['lessonid']
            lesson_object = models.Lesson.objects.get(lesson_id=lesson_id)
            if classroom_id:
                classroom_object = models.Classroom.objects.get(classroom_id=classroom_id)
                models.Booking.objects.get_or_create(
                    date=booking_date,
                    period=period,
                    lesson=lesson_object,
                    classroom=classroom_object
                )
            else:
                models.Booking.objects.get_or_create(
                    date=booking_date,
                    period=period,
                    lesson=lesson_object,
                    classroom=None
                )

        msg = {'message': 'all bookings are successfully stored'}
        return Response(msg, status=status.HTTP_201_CREATED)


        #
        # lessons = {}
        # for child in root.iter('lesson'):
        #     lessons[child.attrib['id']] = {
        #         'teacher_id': child.attrib['teacherids'],
        #         'subject_id': child.attrib['subjectid'],
        #         'group_id': child.attrib['classids'].split(',')[0]
        #     }
        #
        # for child in root.iter('card'):
        #     booking_date = get_date_for_day(child.attrib['days'])
        #     period = child.attrib['period']
        #     group_id = lessons[child.attrib['lessonid']]['group_id']
        #     classroom_id = child.attrib['classroomids'].split(',')[0]
        #     teacher_id = lessons[child.attrib['lessonid']]['teacher_id']
        #     subject_id = lessons[child.attrib['lessonid']]['subject_id']
        #
        #     classroom_object = models.Classroom.objects.get(classroom_id=classroom_id)
        #     print(classroom_id)
        #     group_object = models.Group.objects.get(group_id=group_id)
        #     teacher_object = models.Teacher.objects.get(teacher_id=teacher_id)
        #     subject_object = models.Subject.objects.get(subject_id=subject_id)
        #
        #     models.Booking.objects.get_or_create(
        #         date=booking_date,
        #         period=period,
        #         group=group_object,
        #         classroom=classroom_object,
        #         teacher=teacher_object,
        #         subject=subject_object
        #     )
        #
        # msg = {'success': 'data is successfully stored'}
        # return Response(msg, status=status.HTTP_201_CREATED)


DAYS_MAP = {
    '100000': 0,
    '010000': 1,
    '001000': 2,
    '000100': 3,
    '000010': 4,
    '000001': 5,
}



month_map = {
    "января": 1,
    "январь": 1,
    "январ": 1,
    "февраля": 2,
    "февраль": 2,
    "феврал": 2,
    "марта": 3,
    "март": 3,
    "апреля": 4,
    "апрель": 4,
    "апрел": 4,
    "мая": 5,
    "май": 5,
    "июня": 6,
    "июнь": 6,
    "июн": 6,
    "июля": 7,
    "июль": 7,
    "июл": 7,
    "августа": 8,
    "август": 8,
    "сентября": 9,
    "сентябрь": 9,
    "сентябр": 9,
    "октября": 10,
    "октябрь": 10,
    "октябр": 10,
    "ноября": 11,
    "ноябрь": 11,
    "ноябр": 11,
    "декабря": 12,
    "декабрь": 12,
    "декабр": 12
}
def with_word(birth):
    list_data = birth.split(" ")
    y = list_data[0][0:4]
    m = str(month_map[list_data[2]])
    d = str(list_data[1])
    l = [y, m, d]
    ready_data = '-'.join(l)
    return ready_data

def with_number(birth):
    data = birth.split(".")
    if data[2] in ["03", "02", "01", "00"]:
        y = "20" + data[2]
    else:
        y = "19" + data[2]
    m = data[1]
    if m[0] == "0":
        m = m.replace(m[0], "")
    d = data[0]
    if d[0] == "0":
        if len(d) == 2:
            d = d.replace(d[0], "")
        elif len(d) == 3:
            d = d.replace(d[0:2], "")
    l = [y, m, d]
    ready_data = "-".join(l)
    return ready_data

def default(birth):  # 01,05,2002    -> 2002-5-1
    l = birth.split(",")
    y = l[2]
    m = l[1]
    if len(m[0]) == 0:
        m = m.replace(m[0], "")
    d = l[0]
    if len(d[0]) == 0:
        d = d.replace(d[0], "")
    lis = [y, m, d]
    ready_data = '-'.join(lis)
    return ready_data

class UserViewSet(ViewSet):
    """manages users"""
    def list(self, request):
        """returns all students in our database"""
        users = get_user_model().objects.all()
        serializer = serializers.UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """handles incoming student list"""
        csv_file = request.FILES['student_data']
        # with open(file=csv_file, mode='r') as file:
        csvf = StringIO(csv_file.read().decode())
        csv_reader = csv.reader(csvf, delimiter=';')
        ctr = 0
        for row in csv_reader:
            print(row)
            if ctr == 0:
                ctr += 1
                continue
            else:
                if (len(row[3]) == 10 or len(row[3]) == 12) and row[3][-1].isnumeric():  # 03, 10, 1992
                    date_of_birth = default(row[3])
                else:
                    if len(row[3]) > 8:  # with word
                        date_of_birth = with_word(row[3])
                    elif len(row[3]) == 8:
                        date_of_birth = with_number(row[3])
                    else:
                        date_of_birth = None
            first_name = row[2]
            last_name = row[1]
            username = row[0]
            date_of_birth = date_of_birth
            model = get_user_model()
            model.objects.get_or_create(username=username,
                                        defaults={'date_of_birth': date_of_birth,
                                                  'first_name': first_name,
                                                  'last_name': last_name
                                        }
                                        )
        msg = {
            "message": "student list have successfully been stored"
        }
        return Response(msg, status=status.HTTP_201_CREATED)