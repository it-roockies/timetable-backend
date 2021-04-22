import uuid
import csv
from django.core.files.uploadedfile import InMemoryUploadedFile
from . import models
from io import StringIO


def code():
    x = uuid.uuid1()
    return str(x)


def import_teacher_lesson(csv_file):
    if type(csv_file) == InMemoryUploadedFile:
        csvf = StringIO(csv_file.read().decode('utf-8-sig'))
    else:
        csvf = StringIO(csv_file)
    reader = csv.reader(csvf, delimiter=',')
    full_teachers = []
    full_subjects = []
    full_data = []
    ctr = 1
    for row in reader:
        if ctr == 1:
            ctr += 1
            continue
        full_teachers.append(row[7:])
        full_data.append(row[4:])
        if row[6] == '':
            continue
        full_subjects.append(row[6])
    imported_teachers = []
    # prepare valid data for teacher object
    for teachers in full_teachers:
        for teacher in teachers:
            helper = {}
            if teacher != '':
                helper['teacher_id'] = code()
                if len(teacher.split(' ')) == 1:
                    helper['first_name'] = teacher.split(' ')[0]
                    helper['last_name'] = teacher.split(' ')[0]
                else:
                    helper['first_name'] = teacher.split(' ')[0]
                    helper['last_name'] = teacher.split(' ')[1]
                imported_teachers.append(helper)
    # import teacher
    for teacher in imported_teachers:
        if not models.Teacher.objects.filter(firstname__iexact=teacher['first_name'],
                                             lastname__iexact=teacher['last_name']).exists():
            models.Teacher.objects.create(firstname=teacher['first_name'],
                                          lastname=teacher['last_name'],
                                          teacher_id=teacher['teacher_id']
                                          )
    # prepare subject objects to be imported
    imported_subjects = []
    for subject in full_subjects:
        imported_subjects.append(dict(
            subject_id=code(),
            name=subject,
        ))

    # import subject
    for s in imported_subjects:
        if not models.Subject.objects.filter(name__iexact=s['name']).exists():
            models.Subject.objects.create(name=s['name'],
                                          subject_id=s['subject_id']
                                          )
    # prepare data for subject teacher object
    for data in full_data:  # [level, term, subject, teachers]
        if data[0] != '':
            level = data[0]
        else:
            level = ''
        if data[1] == '':
            break
        else:
            term = int(float(data[1]))
        if data[2] == '':
            break
        else:
            subject = data[2]
        for teacher in data[3:]:
            if teacher == '':
                continue
            else:
                if len(teacher.split(' ')) == 1:

                    firstname = teacher.split(' ')[0]
                    lastname = teacher.split(' ')[0]
                else:
                    firstname = teacher.split(' ')[0]
                    lastname = teacher.split(' ')[1]
                print(firstname, lastname)
                teacher_obj = models.Teacher.objects.filter(firstname__iexact=firstname, lastname__iexact=lastname)[0]
                print(subject)
                subject_obj = models.Subject.objects.filter(name__iexact=subject)[0]
                models.TeacherSubject.objects.create(
                    level=level,
                    term=term,
                    teacher=teacher_obj,
                    subject=subject_obj
                )
