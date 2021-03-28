from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from booking import models

from rest_framework import serializers

class GroupSerializer(serializers.ModelSerializer):
    """Interacts with Group data"""
    class Meta:
        model = models.Group
        fields = [
            'id',
            'name',
        ]

class UserSerializer(serializers.ModelSerializer):
    group = GroupSerializer(many=False)
    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'group',
            'is_staff'
        ]