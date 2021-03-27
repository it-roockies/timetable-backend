from rest_framework import serializers
from . import models
from django.contrib.auth import get_user_model, authenticate


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'username',
            'telegram_id',
            'first_name',
            'last_name',
            'date_of_birth',
            'group'
        ]


    def create(self, validated_data):
        """creates and saves a user"""
        return get_user_model().objects.create_user(**validated_data)



# class AuthTokenSerializer(serializers.Serializer):
#     """Serializes user authentication object"""
#     student_id = serializers.CharField()
#     password = serializers.CharField()
#
#
#     def validate(self, attrs):
#         """checks and authenticates given credential"""
#         student_id = attrs.get('student_id')
#         password = attrs.get('password')
#
#         user = authenticate(
#             request=self.context.get('request'),
#             username=student_id,
#             password=password
#         )
#
#         if not user:
#             msg = 'Unable to authenticate with provided credentials'
#             raise serializers.ValidationError(msg, code='authentication')
#         attrs['user'] = user
#
#         return attrs

class Classroom(serializers.ModelSerializer):

    class Meta:
        model = models.Classroom
        fields = [
            'id',
            'name'
        ]

class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Lesson
        fields = [
            'id',
            'groups',
            'teacher',
            'subject'
        ]

class ClassroomSerializer(serializers.ModelSerializer):
    """Interacts with Room data"""
    class Meta:
        model = models.Classroom
        fields = [
            'id',
            'name',
        ]

class BookingSerializer(serializers.ModelSerializer):
    """A serializer that helps us to serializer booking data """
    lesson = LessonSerializer()
    classroom = ClassroomSerializer()

    class Meta:
        model = models.Booking
        fields = [
            'id',
            'date',
            'period',
            'lesson',
            'classroom'
        ]

class CardSerializer(serializers.Serializer):
    period = serializers.CharField(max_length=255)
    date = serializers.DateField()
    classroom = serializers.CharField(max_length=255)
    teacher = serializers.CharField(max_length=255)
    subject = serializers.CharField(max_length=255)
    group = serializers.CharField(max_length=255)


class TeacherSerializer(serializers.ModelSerializer):
    """Interacts with Tutor data"""
    class Meta:
        model = models.Teacher
        fields = [
            'id',
            'firstname',
            'lastname',
            'short',
        ]


class SubjectSerializer(serializers.ModelSerializer):
    """Interacts with Module data"""
    class Meta:
        model = models.Subject
        fields = [
            'id',
            'name',
        ]

class GroupSerializer(serializers.ModelSerializer):
    """Interacts with Group data"""
    class Meta:
        model = models.Group
        fields = [
            'id',
            'name',
        ]
