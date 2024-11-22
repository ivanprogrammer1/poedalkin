from rest_framework import serializers

from .models import User

class UserObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'personal_data', 'street', 'house', 'apartment', 'entrance', 'floor', 'door_code']