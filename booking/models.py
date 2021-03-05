from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    """Just customizing default django's user."""
    pass

class Group(models.Model):
    group_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        """returns group name"""
        return self.name

class Subject(models.Model):
    subject_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=256)
    short = models.CharField(max_length=5)


    def __str__(self):
        """returns module name"""
        return self.short


class Teacher(models.Model):
    teacher_id = models.CharField(max_length=255, unique=True, editable=False)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=256)
    short = models.CharField(max_length=3)
    subjects = models.ManyToManyField(Subject, related_name="teachers", through='TeacherSubject')


    def __str__(self):
        """returns professors full name"""
        full_name = self.firstname + ' ' + self.lastname
        return full_name


class TeacherSubject(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('teacher', 'subject'), )


class Classroom(models.Model):
    classroom_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(max_length=255)
    # capacity = models.IntegerField()

    def __str__(self):
        """returns title of the room"""
        return self.title


class Booking(models.Model):
    FIRST   = 1
    SECOND  = 2
    THIRD   = 3
    FOURTH  = 4
    FIFTH   = 5
    period_of_lesson = [
        (FIRST, '9:00-10:00'),
        (SECOND, '10:20-11:20'),
        (THIRD, '12:00-13:00'),
        (FOURTH, '13:20-14:20'),
        (FIFTH, '14:40-15:40')
    ]
    date = models.DateField()
    period = models.CharField(max_length=1, choices=period_of_lesson, default=FIRST)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default='group')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, default='classroom')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, default='teacher')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, default='subject')


class Day(models.Model):
    E   = '11111'
    MO  = '100000'
    TU  = '010000'
    WE  = '001000'
    TH  = '000100'
    FR  = '000010'
    SA  = '000001'
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


