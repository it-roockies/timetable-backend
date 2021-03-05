from rest_framework import serializers
from . import models
from django.contrib.auth import get_user_model


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
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
            'starts_at',
            'ends_at',
            'group',
            'room',
            'tutor',
            'module'
        ]

class TutorSerializer(serializers.ModelSerializer):
    """Interacts with Tutor data"""
    class Meta:
        model = models.Tutor
        fields = [
            'first_name',
            'last_name',
            'module'
        ]

class RoomSerializer(serializers.ModelSerializer):
    """Interacts with Room data"""
    class Meta:
        model = models.Room
        fields = [
            'title',
        ]

class ModuleSerializer(serializers.ModelSerializer):
    """Interacts with Module data"""
    class Meta:
        model = models.Module
        fields = [
            'name',
        ]

class GroupSerializer(serializers.ModelSerializer):
    """Interacts with Group data"""
    class Meta:
        model = models.Group
        fields = [
            'name',
        ]
