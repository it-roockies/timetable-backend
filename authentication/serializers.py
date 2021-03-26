from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'group',
            'is_staff'
        ]