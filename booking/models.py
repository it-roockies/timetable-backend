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

class Module(models.Model):
    subject_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=256)
    short_name = models.CharField(max_length=5)


    def __str__(self):
        """returns module name"""
        return self.short_name


class Tutor(models.Model):
    teacher_id = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=256)
    module = models.ManyToManyField(Module)
    short_name = models.CharField(max_length=3)


    def __str__(self):
        """returns professors full name"""
        full_name = self.first_name + ' ' + self.last_name
        return full_name


class Room(models.Model):
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
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default='room')
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, default='tutor')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, default='module')


    # def __str__(self):
    #     """returns time period"""
    #     time_period = str(self.starts_at) + " - " + str(self.ends_at)
    #     return time_period
