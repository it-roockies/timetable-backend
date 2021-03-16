from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.authtoken.models import Token

class UserSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = get_user_model()
        fields = [
            'faculty',
            'education_year',
        ]
        read_only_fields= [ 'id' ]

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key