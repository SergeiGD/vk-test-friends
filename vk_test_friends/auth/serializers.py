from rest_framework import serializers

from users.models import CustomUser


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

        return super().validate(data)

    def create(self, validated_data):
        """
        Переопределенный метод create, для вызова create_user
        """
        data = {
            'email': validated_data['email'],
            'first_name': validated_data.get('first_name', ''),
            'last_name': validated_data.get('last_name', ''),
            'password': validated_data['password1'],
            'is_staff': False,
            'is_active': False,
            'is_superuser': False,
        }
        user = CustomUser.objects.filter(email=data['email'], is_active=False).first()
        if user is not None:
            # если пользователь уже регистрировался, но так и не подтвердил аккаунт, то просто обновим данные
            user.first_name = data['first_name']
            user.last_name = data['last_name']
            user.save()
            user.set_password(data['password'])
            return user
        return CustomUser.objects.create_user(**data)


class VerifyAccountSerializer(serializers.Serializer):
    """
    Сериалайзер для подтверждения регистрации
    """
    token = serializers.CharField(write_only=True)
    encoded_id = serializers.CharField(write_only=True)


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
