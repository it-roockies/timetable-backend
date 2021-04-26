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


def get_date_for_day(day, week: str):
    start = datetime.strptime(f"{week}-1", "%Y-W%W-%w").date()  # starting of week's date
    result = start + timedelta(days=DAYS_MAP[day])
    return result


def delete_week_cards(week: str):
    start = datetime.strptime(f"{week}-1", "%Y-W%W-%w").date()
    end = start + timedelta(days=7)
    bookings = models.Booking.objects.filter(date__range=[start, end])
    bookings.delete()


"""takes file and stores information into database"""


def import_edupage():
    timetables = get_timetables()
    tt_num = timetables[0]["tt_num"]
    data = get_timetable_data(tt_num)

    # delete_week_cards(week)

    # Import Subjects
    _subjects = next(table["data_rows"] for table in data if table["id"] == "subjects")
    subjects = {[subject["id"]]: models.Subject.objects.get(short=subject["short"]) for subject in _subjects}

    # Import Teachers
    _teachers = next(table["data_rows"] for table in data if table["id"] == "teachers")
    teachers = {[teacher["id"]]: models.Teacher.objects.get(short=teacher["short"]) for teacher in _teachers}

    # import Groups
    _groups = next(table["data_rows"] for table in data if table["id"] == "classes")
    groups = {[group["id"]]: models.Group.objects.get(short=group["short"]) for group in _groups}

    # import Classrooms
    _classrooms = next(table["data_rows"] for table in data if table["id"] == "classrooms")
    classrooms = {
        [classroom["id"]]: models.Classroom.objects.get(short=classroom["short"]) for classroom in _classrooms
    }

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
