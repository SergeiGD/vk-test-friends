from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from friend_requests.models import FriendRequest
from friend_requests.services import get_active_outcoming_requests
from users.models import CustomUser


class BaseRequestsSerializer(serializers.ModelSerializer):
    """
    Базовый сериалайзер заявок
    """
    date_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'date_created', 'url']


class IncomingRequestsSerializer(BaseRequestsSerializer):
    """
    Сериалайзер входящих заявок
    """
    sender_url = serializers.HyperlinkedRelatedField(
        view_name='user',
        read_only=True,
        source='sender',
    )
    url = serializers.HyperlinkedIdentityField(view_name='incoming_request')
    class Meta(BaseRequestsSerializer.Meta):
        fields = [
            *BaseRequestsSerializer.Meta.fields,
            'sender',
            'sender_url',
        ]


class OutcomingRequestsSerializer(BaseRequestsSerializer):
    """
    Сериалайзер исходящих заявок
    """
    target_url = serializers.HyperlinkedRelatedField(
        view_name='user',
        read_only=True,
        source='target',
    )
    url = serializers.HyperlinkedIdentityField(view_name='outcoming_request')

    class Meta(BaseRequestsSerializer.Meta):
        fields = [
            *BaseRequestsSerializer.Meta.fields,
            'target',
            'target_url',
        ]

    def validate(self, data):
        target = data['target']
        # берем sender из контекста
        sender = self.context.get('sender')

        if sender == target:
            # если запрос отправлен самому себе
            raise ValidationError({
                'target': 'Нельзя отправить запрос самому себе',
            })

        if CustomUser.objects.filter(
                friends__pk=target.id, pk=sender.pk
        ).exists():
            # если уже друзья
            raise ValidationError({
                'target': 'Нельзя отправить запрос пользователю, с котором вы уже друзья',
            })

        if get_active_outcoming_requests(sender).filter(
                target=target,
        ).exists():
            # если уже есть запрос от этого пользователя
            raise ValidationError({
                'target': 'Уже есть активный запрос от этому пользователю',
            })

        return super().validate(data)
