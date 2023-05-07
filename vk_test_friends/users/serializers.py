from rest_framework import serializers

from users.models import CustomUser


class UsersSerializer(serializers.HyperlinkedModelSerializer):
    """
    Сериалайзер пользователей
    """
    url = serializers.HyperlinkedIdentityField(view_name='user')
    date_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'url', 'email', 'first_name', 'last_name', 'date_created', ]
