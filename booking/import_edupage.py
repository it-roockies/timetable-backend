import logging
import requests

from datetime import date, timedelta, datetime
from django.core.files.uploadedfile import InMemoryUploadedFile

from . import models
from django.db.models import Count


logger = logging.getLogger(__name__)


def request(*, method: str, url: str, data=None):
    try:
        response = requests.request(method=method, url=url, json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.exception(str(e))
        if hasattr(e, "response"):
            logger.debug(e.response.text)
        return None


def get_timetables():
    data = request(
        method="POST",
        url="https://ttpu.edupage.org/timetable/server/ttviewer.js?__func=getTTViewerData",
        data={"__args": [None, 2020], "__gsh": "00000000"},
    )
    return data["r"]["regular"]["timetables"]


def get_timetable_data(tt_num):
    data = request(
        method="POST",
        url="https://ttpu.edupage.org/timetable/server/regulartt.js?__func=regularttGetData",
        data={"__args": [None, tt_num], "__gsh": "00000000"},
    )
    return data["r"]["dbiAccessorRes"]["tables"]


DAYS_MAP = {
    "100000": 0,
    "010000": 1,
    "001000": 2,
    "000100": 3,
    "000010": 4,
    "000001": 5,
}


"""returns date according to week number. 0 is monday (starts from current week's day)"""


def get_week_start(week):
    return datetime.strptime(f"{week}-1", "%Y-W%W-%w").date()


def get_date_for_day(day, week: str):
    start = get_week_start(week)  # starting of week's date
    result = start + timedelta(days=DAYS_MAP[day])
    return result


def delete_week_cards(week: str):
    start = get_week_start(week)
    end = start + timedelta(days=7)
    bookings = models.Booking.objects.filter(date__range=[start, end])
    bookings.delete()


def delete_week_cards(week: str):
    start = get_week_start(week)
    end = start + timedelta(days=7)
    bookings = models.Booking.objects.filter(date__range=[start, end])
    bookings.delete()


def get_subjects_or_ignore(_subjects):
    subjects = {}
    for _subject in _subjects:
        try:
            subjects[_subject["id"]] = models.Subject.objects.get(short=_subject["short"])
        except (models.Subject.DoesNotExist, models.Subject.MultipleObjectsReturned):
            print(f'Subject with short {_subject["short"]} not found')
    return subjects


def get_teachers(_teachers):
    teachers = {}
    for _teacher in _teachers:
        try:
            teachers[_teacher["id"]] = models.Teacher.objects.get(short=_teacher["short"])
        except (models.Teacher.DoesNotExist, models.Teacher.MultipleObjectsReturned):
            print(f'Subject with short {_teacher["short"]} not found')
    return teachers


def import_edupage(week):
    # Find timetable id for given week
    timetables = get_timetables()
    datefrom = get_week_start(week).isoformat()

    tt_num = next(table["tt_num"] for table in timetables if table["datefrom"] == datefrom)

    data = get_timetable_data(tt_num)

    delete_week_cards(week)

    # Import Subjects
    _subjects = next(table["data_rows"] for table in data if table["id"] == "subjects")
    subjects = get_subjects_or_ignore(_subjects)

    # Import Teachers
    _teachers = next(table["data_rows"] for table in data if table["id"] == "teachers")
    teachers = get_teachers(_teachers)

    # import Groups
    _groups = next(table["data_rows"] for table in data if table["id"] == "classes")
    groups = {group["id"]: models.Group.objects.get(name=group["name"]) for group in _groups}

    # import Classrooms
    _classrooms = next(table["data_rows"] for table in data if table["id"] == "classrooms")
    classrooms = {classroom["id"]: models.Classroom.objects.get(name=classroom["name"]) for classroom in _classrooms}

    # import Lessons
    _lessons = next(table["data_rows"] for table in data if table["id"] == "lessons")
    lessons = {}
    for _lesson in _lessons:
        lesson_subject = subjects[_lesson["subjectid"]]
        lesson_teachers = [teachers[_id] for _id in _lesson["teacherids"]]
        lesson_groups = [groups[_id] for _id in _lesson["classids"]]

        lessons[_lesson["id"]] = (
            models.Lesson.objects.filter(subject=lesson_subject)
            .filter(teachers__in=lesson_teachers)
            .annotate(num_teachers=Count("teachers"))
            .filter(num_teachers=len(lesson_teachers))
            .filter(groups__in=lesson_groups)
            .annotate(num_groups=Count("groups"))
            .filter(num_groups=len(lesson_groups))
            .get()
        )

    # # import Booking
    # for child in root.iter("card"):
    #     booking_date = get_date_for_day(day=child.attrib["days"], week=week)
    #     period = child.attrib["period"]
    #     classroom_id = child.attrib["classroomids"]
    #     lesson_id = child.attrib["lessonid"]
    #     lesson_object = models.Lesson.objects.get(lesson_id=lesson_id)
    #     if classroom_id:
    #         classroom_object = models.Classroom.objects.get(classroom_id=classroom_id)
    #         models.Booking.objects.get_or_create(
    #             date=booking_date, period=period, lesson=lesson_object, classroom=classroom_object
    #         )
    #     else:
    #         models.Booking.objects.get_or_create(date=booking_date, period=period, lesson=lesson_object, classroom=None)
