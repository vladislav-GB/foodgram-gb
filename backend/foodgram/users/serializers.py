from rest_framework import serializers
from api.serializers import Base64ImageField
from .models import User

class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ['avatar']