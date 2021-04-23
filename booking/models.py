from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, AbstractUser
from django.utils import timezone

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
    attended_questionnaire = models.IntegerField(default=0)

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
    short = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        """returns module name"""
        return self.name


class Teacher(models.Model):
    teacher_id = models.CharField(max_length=255, unique=True, editable=False)
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    short = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        """returns professors full name"""
        full_name = self.firstname + ' ' + self.lastname
        return full_name

class TeacherSubject(models.Model):
    level = models.IntegerField(blank=True, null=True)
    term = models.IntegerField(blank=True, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, blank=True, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

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


class Event(models.Model):
    name = models.CharField(max_length=255, unique=True)
    from_time = models.DateTimeField(default=timezone.now)
    to_time = models.DateTimeField(default=timezone.now)
    special = models.BooleanField(default=False)

    def __str__(self):
        """returns object as string representation"""
        return self.name


class EventMember(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    responsible = models.BooleanField(default=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    def __str__(self):
        """returns object as string representation by user"""
        return self.user


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
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, default='lesson', blank=True, null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, blank=True, null=True)
