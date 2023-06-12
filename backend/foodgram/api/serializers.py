from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from users.models import CustomUser, Subscribe


class SubscribeSerializer(serializer.Serializer):
    """Сериалайзер Users."""

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


