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
        extra_kwargs = {
            'id': {'read_only': False},
            'name': {'read_only': True}
        }


class UserSerializer(serializers.ModelSerializer):
    group = GroupSerializer()
    class Meta:
        model = get_user_model()
        fields = [
            'id',
            'group',
            'is_staff'
        ]

    def validate_group(self, value):
        """
        Check that the group is exist.
        """
        if 'id' not in value:
            raise serializers.ValidationError("group should contain id")
        try:
            return models.Group.objects.get(id=value.get('id'))
        except models.Group.DoesNotExist:
            raise serializers.ValidationError('Group does not exist')

    def update(self, instance, validated_data):
        print(validated_data.get('group', None))
        instance.group = validated_data.get('group', instance.group)
        instance.save()
        return instance
