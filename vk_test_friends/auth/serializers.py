from rest_framework import serializers
import logging

from users.models import CustomUser

logger = logging.getLogger('auth_logger')


class SingUpSerializer(serializers.ModelSerializer):
    """
    Сериалайзер для регистрации пользователей
    """
    password1 = serializers.CharField(min_length=6, write_only=True)
    password2 = serializers.CharField(min_length=6, write_only=True)
    # определим вручную email, чтоб не проводилась автоматическая валидация модели на уникальность
    email = serializers.EmailField()

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'password1', 'password2', ]

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({
                'password': 'Пароли не совпадают'
            })
        if CustomUser.objects.filter(email=data['email'], is_active=True).exists():
            logger.info(f'попытка регистрации уже активного аккаунта {data["email"]}')
            raise serializers.ValidationError({
                'email': 'Уже есть активный пользователь с таким адресом эл. почты'
            })

        return super().validate(data)


class VerifyAccountSerializer(serializers.Serializer):
    """
    Сериалайзер для подтверждения регистрации
    """
    token = serializers.CharField()
    encoded_id = serializers.CharField()


class RequestResetPasswordSerializer(serializers.Serializer):
    """
    Сериалайзер для запроса сброса пароля
    """
    email = serializers.EmailField()

    def validate(self, data):
        # проверяем есть ли активный пользователь с такой почтой
        if not CustomUser.objects.filter(
            email=data['email'],
            is_active=True,
        ).exists():
            logger.info(f'попытка сброса пароля для незарегистрированного/неактивного аккаунта {data["email"]}')
            raise serializers.ValidationError({
                'email': 'Не найден активный пользователь с таким адресом эл. почты'
            })

        return data


class ConfirmResetPasswordSerializer(VerifyAccountSerializer):
    """
    Сериалайзер для подтверждения сброса пароля
    """
    password1 = serializers.CharField(min_length=6, write_only=True)
    password2 = serializers.CharField(min_length=6, write_only=True)

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError({
                'password': 'Пароли не совпадают'
            })

        return super().validate(data)
