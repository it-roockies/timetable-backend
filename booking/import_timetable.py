import xml.etree.ElementTree as ET
from datetime import date, timedelta, datetime
from django.core.files.uploadedfile import InMemoryUploadedFile

from . import models

DAYS_MAP = {
    '100000': 0,
    '010000': 1,
    '001000': 2,
    '000100': 3,
    '000010': 4,
    '000001': 5,
}


"""returns date according to week number. 0 is monday (starts from current week's day)"""
def get_date_for_day(day, week: str):
    start = datetime.strptime(f"{week}-1", "%Y-W%W-%w").date()  # starting of week's date
    result = start + timedelta(days=DAYS_MAP[day])
    return result

"""takes file and stores information into database"""
def import_timetable(week, _file):
    if type(_file) == InMemoryUploadedFile:
        root = ET.fromstring(_file.read())
    else:
        root = ET.fromstring(_file)

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
        booking_date = get_date_for_day(day=child.attrib['days'], week=week)
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
