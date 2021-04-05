from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser


# Create your models here.

# class UserManager(BaseUserManager):
#     """manages our custom user model"""
#     def create_user(self, student_id, password=None, **extra_fields):
#         """creates, saves and returns a user"""
#         if not student_id:
#             raise ValueError("Every user must have student id")
#
#         user = self.model(student_id=student_id, **extra_fields)
#         user.save(using=self._db)
#
#         return user
#
#     def create_superuser(self, telegram_id, password, **extra_fields):
#         """create a super user"""
#
#         user = self.create_user(telegram_id=telegram_id, password=password, **extra_fields)
#         user.is_superuser = True
#         user.is_staff = True
#
#         user.save(using=self._db)
#
#         return user


class User(AbstractUser):
    """Just customizing default django's user."""
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    telegram_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    date_of_birth = models.DateField(max_length=255, blank=True, null=True)
    group = models.ForeignKey('Group', on_delete=models.CASCADE, null=True, blank=True)


    def __str__(self):
        return self.username


class Message(models.Model):
    message_id = models.CharField(max_length=255, unique=True)
    text = models.CharField(max_length=255)

    def __str__(self):
        return self.message_id


class Group(models.Model):
    group_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    # class_id = models.CharField(max_length=255)

    def __str__(self):
        """returns group name"""
        return self.name


class Subject(models.Model):
    subject_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    short = models.CharField(max_length=5)

    def __str__(self):
        """returns module name"""
        return self.short


class Teacher(models.Model):
    teacher_id = models.CharField(max_length=255, unique=True, editable=False)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    short = models.CharField(max_length=3)
    color = models.CharField(max_length=255)

    def __str__(self):
        """returns professors full name"""
        full_name = self.firstname + ' ' + self.lastname
        return full_name


class Classroom(models.Model):
    classroom_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    # teacher_id = models.CharField(max_length=255)

    # capacity = models.IntegerField()

    def __str__(self):
        """returns title of the room"""
        return self.name

class Lesson(models.Model):
    lesson_id = models.CharField(max_length=255, unique=True)
    groups = models.ManyToManyField(Group)
    teachers = models.ManyToManyField(Teacher)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default='subject')

    def __str__(self):
        return f"{self.subject} ({self.teachers})"


class Booking(models.Model):
    period_of_lesson = [
        ("1", '9:00-10:00'),
        ("2", '10:20-11:20'),
        ("3", '12:00-13:00'),
        ("4", '13:20-14:20'),
        ("5", '14:40-15:40'),
        ("6", '16:00-17:00')
    ]

    date = models.DateField()
    period = models.CharField(max_length=1, choices=period_of_lesson, default='1')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, default='lesson')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, blank=True, null=True)



class Card:
    def __init__(self, period, date, classroom, teacher, subject, group):
        self.period = period
        self.date = date
        self.classroom = classroom
        self.teacher = teacher
        self.subject = subject
        self.group = group




class Day(models.Model):
    E = '11111'
    MO = '100000'
    TU = '010000'
    WE = '001000'
    TH = '000100'
    FR = '000010'
    SA = '000001'
    week_days = [
        (E, 'Every day'),
        (MO, 'Monday'),
        (TU, 'Tuesday'),
        (WE, 'Wednesday'),
        (TH, 'Thursday'),
        (FR, 'Friday'),
        (SA, 'Saturday')
    ]
    day_id = models.CharField(max_length=255, unique=True)
    day = models.CharField(max_length=6, choices=week_days, default=MO)


class Week(models.Model):
    All = "111111111111111"
    A = "100000000000000"
    B = "010000000000000"
    C = "001000000000000"
    D = "000100000000000"
    E = "000010000000000"
    F = "000001000000000"
    G = "000000100000000"
    H = "000000010000000"
    I = "000000001000000"
    J = "000000000100000"
    K = "000000000010000"
    L = "000000000001000"
    M = "000000000000100"
    N = "000000000000010"
    O = "000000000000001"

    week_choices = [

        (All, "All weeks"),
        (A, "Week A"),
        (B, "Week B"),
        (C, "Week C"),
        (D, "Week D"),
        (E, "Week E"),
        (F, "Week F"),
        (G, "Week G"),
        (H, "Week H"),
        (I, "Week I"),
        (J, "Week J"),
        (K, "Week K"),
        (L, "Week L"),
        (M, "Week M"),
        (O, "Week O"),
        (N, "Week N")
    ]
    week = models.CharField(max_length=15, choices=week_choices, default=A)
    week_id = models.CharField(max_length=255, unique=True)


class Term(models.Model):
    YR = '11'
    T1 = '10'
    T2 = '01'

    term_choices = [
        (YR, 'Whole year'),
        (T1, 'Term 1'),
        (T2, 'Term 2')
    ]
    term_id = models.CharField(max_length=255, unique=True)
    term = models.CharField(max_length=2, choices=term_choices, default=T1)

# class Card(models.Model):
#     FIRST = 1
#     SECOND = 2
#     THIRD = 3
#     FOURTH = 4
#     FIFTH = 5
#     period_of_lesson = [
#         (FIRST, '9:00-10:00'),
#         (SECOND, '10:20-11:20'),
#         (THIRD, '12:00-13:00'),
#         (FOURTH, '13:20-14:20'),
#         (FIFTH, '14:40-15:40')
#     ]
#     booking_id = models.CharField(max_length=255)
#     classroom_id = models.CharField(max_length=255)
#     period = models.CharField(max_length=1, choices=period_of_lesson, default=FIRST)
#     day = models.CharField(max_length=255)
#     week = models.CharField(max_length=255)
#     term = models.CharField(max_length=255)
