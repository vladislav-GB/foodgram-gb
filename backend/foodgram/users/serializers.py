from api.serializers import Base64ImageField
from rest_framework import serializers

from .models import User


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ["avatar"]

    def validate(self, data):
        if self.context["request"].method == "PUT" and "avatar" not in data:
            raise serializers.ValidationError({"avatar": "Это поле обязательно."})
        return data
