from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    """Just customizing default django's user."""
    pass





class Group(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        """returns group name"""
        return self.name

class Module(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        """returns module name"""
        return self.name


class Tutor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=256)
    module = models.OneToOneField(Module, on_delete=models.CASCADE, related_name='tutor')

    def __str__(self):
        """returns professors full name"""
        full_name = self.first_name + ' ' + self.last_name
        return full_name


class Room(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        """returns title of the room"""
        return self.title

class Booking(models.Model):
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, default='group')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, default='room')
    tutor = models.ForeignKey(Tutor, on_delete=models.CASCADE, default='tutor')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, default='module')


    # def __str__(self):
    #     """returns time period"""
    #     time_period = str(self.starts_at) + " - " + str(self.ends_at)
    #     return time_period
