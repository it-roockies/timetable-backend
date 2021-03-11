from rest_framework import serializers
from . import models
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'username',
            'email',
            'password'
        ]

    def create(self, validated_data):
        """creates and saves a user"""
        return get_user_model().objects.create_user(**validated_data)



class BookingSerializer(serializers.ModelSerializer):
    """A serializer that helps us to serializer booking data """
    class Meta:
        model = models.Booking
        fields = [
            'id',
            'date',
            'period',
            'group',
            'classroom',
            'teacher',
            'subject'
        ]

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

class ClassroomSerializer(serializers.ModelSerializer):
    """Interacts with Room data"""
    class Meta:
        model = models.Classroom
        fields = [
            'id',
            'name',
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
