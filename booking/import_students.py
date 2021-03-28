import re
import csv
from io import StringIO
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import InMemoryUploadedFile

from .models import Group

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
    "сентябяря": 9,
    "октября": 10,
    "октябрь": 10,
    "октябр": 10,
    "ноября": 11,
    "ноябрь": 11,
    "ноябр": 11,
    "декабря": 12,
    "декабрь": 12,
    "декабр": 12,
    "декаюря": 12
}

def double_number(number):
    return number if len(number) > 1 else f'0{number}'

def parse_month(month):
    if month not in month_map:
        raise ValueError(f'month "{month}" not found')
    return double_number(str(month_map[month]))

def with_word_1(year:str, day:str, month:str):
    return '-'.join([year, parse_month(month), double_number(day)])

def with_number_1(day:str, month:str, year:str):
    if len(day) > 2:
        day = str(int(day))
    return '-'.join([year, double_number(month), double_number(day)])

def with_number_2(day:str, month:str, year:str):
    if year in ["05", "04", "03", "02", "01", "00"]:
        year = "20" + year
    else:
        year = "19" + year

    return '-'.join([year, double_number(month), double_number(day)])


def get_date_of_birth(raw_str):
    if raw_str is None or raw_str == '':
        return None

    # 1999, 25 ноября
    res = re.match(r'(^\d{4})\s{0,1}[\.\,]\s{0,1}(\d{1,2})\s{0,1}(\w+)\s{0,1}$', raw_str)
    if res:
        return with_word_1(res.group(1), res.group(2), res.group(3))

    # 02.01.2003
    res = re.match(r'(^\d{1,3})[\.\,](\d{1,2})[\.\,](\d{4})\.{0,1}$', raw_str)
    if res:
        return with_number_1(res.group(1), res.group(2), res.group(3))

    # 02.01.03
    res = re.match(r'(^\d{1,2})\.(\d{1,2})\.(\d{1,2})$', raw_str)
    if res:
        return with_number_2(res.group(1), res.group(2), res.group(3))

    raise ValueError(f'Unknown date format {raw_str}')


def get_group_name(group_name):
    if group_name is None or group_name == '':
        return None

    if group_name == "IT-17":
        return "IT1-17"
    
    if group_name == "CIE-17":
        return "CIE1-17"
    
    if group_name == "E-17":
        return ''

    return group_name


"""handles incoming student list"""
def import_students(csv_file):
    if type(csv_file) == InMemoryUploadedFile:
        csvf = StringIO(csv_file.read())
    else:
        csvf = StringIO(csv_file)
    csv_reader = csv.reader(csvf, delimiter=';')
    ctr = 0

    for row in csv_reader:
        if ctr == 0:
            ctr = 1
            continue

        username = row[0]
        group_name = get_group_name(row[1])

        last_name = row[2]
        first_name = row[3]
        # middle_name = row[4]
        date_of_birth = get_date_of_birth(row[5])

        model = get_user_model()
        user, created = model.objects.get_or_create(
            username=username,
            defaults={
                'date_of_birth': date_of_birth,
                'first_name': first_name,
                'last_name': last_name
            }
        )

        # Date of birth is provided
        if not created and user.date_of_birth is None and date_of_birth is not None:
            user.date_of_birth = date_of_birth

        # Group is provided
        if group_name and user.group is None:
            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                raise ValueError(f'Group does not exists {group_name}')

            user.group = group

        user.save()