from django.contrib.sites.shortcuts import get_current_site
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from .serializers import (
    SingUpSerializer, VerifyAccountSerializer, RequestResetPasswordSerializer, ConfirmResetPasswordSerializer
)
from .services import send_sing_up_email, verify_account, send_reset_password_email, verify_reset_password, sing_up_user
from users.models import CustomUser


class SingUpView(GenericAPIView):
    """
    Регистрации пользователя
    """
    serializer_class = SingUpSerializer

    @extend_schema(
        responses={
            '201': OpenApiResponse(
                description='Аккаунт создан',
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        'Аккаунт создан',
                        value={
                            'detail': 'На почту отправлено письмо для подтверждения регистрации',
                        },
                    ),
                ],
            ),
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = sing_up_user(serializer.validated_data)

        # отправляем письмо с подтверждением регистрации
        send_sing_up_email(user, get_current_site(request).domain)

        return Response({
            'detail': 'На почту отправлено письмо для подтверждения регистрации',
        }, status=status.HTTP_201_CREATED)


class VerifyAccountAPIView(GenericAPIView):
    """
    Подтверждения регистрации
    """
    serializer_class = VerifyAccountSerializer

    @extend_schema(
        responses={
            '200': OpenApiResponse(
                description='Аккаунт успешно подтвержден',
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        'Аккаунт успешно подтвержден',
                        value={
                            'detail': 'Аккаунт успешно подтвержден',
                        },
                    ),
                ],
            ),
            '400': OpenApiResponse(
                description='Ошибка подтверждения',
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        'Ошибка подтверждения',
                        value={
                            'detail': 'Возникла ошибка при подтверждении аккаунта. Проверьте корректность ссылки',
                        },
                    ),
                ],
            ),
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # получаем токен и закодированное id пользователя
        token = serializer.validated_data['token']
        encoded_id = serializer.validated_data['encoded_id']

        if verify_account(token, encoded_id):
            # если успешно подтвердили
            return Response({
                'detail': 'Аккаунт успешно подтвержден',
            }, status=status.HTTP_200_OK)
        else:
            # если возникла ошибка при подтверждении
            return Response({
                'detail': 'Возникла ошибка при подтверждении аккаунта. Проверьте корректность ссылки',
            }, status=status.HTTP_400_BAD_REQUEST)


class RequestResetPasswordAPIView(GenericAPIView):
    """
    Запроса сброса пароля
    """
    serializer_class = RequestResetPasswordSerializer

    @extend_schema(
        responses={
            '200': OpenApiResponse(
                description='Успешный запрос',
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        'Успешный запрос',
                        value={
                            'detail': 'На почту отправлено письмо для подтверждения сброса пароля',
                        },
                    ),
                ],
            ),
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        # получаем пользователя с указанной почтой (проверка, что он существует уже есть в сериалайзере)
        user = CustomUser.objects.get(email=email)

        # отправляем письмо с подтверждением регистрации
        send_reset_password_email(user, get_current_site(request).domain)

        return Response({
            'detail': 'На почту отправлено письмо для подтверждения сброса пароля',
        }, status=status.HTTP_200_OK)


class ConfirmResetPasswordAPIView(GenericAPIView):
    """
    Подтверждения сброса пароля
    """
    serializer_class = ConfirmResetPasswordSerializer

    @extend_schema(
        responses={
            '200': OpenApiResponse(
                description='Пароль успешно изменен',
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        'Пароль успешно изменен',
                        value={
                            'detail': 'Пароль успешно изменен',
                        },
                    ),
                ],
            ),
            '400': OpenApiResponse(
                description='Ошибка подтверждения',
                response=OpenApiTypes.OBJECT,
                examples=[
                    OpenApiExample(
                        'Ошибка подтверждения',
                        value={
                            'detail': 'Возникла ошибка при подтверждении аккаунта. Проверьте корректность ссылки',
                        },
                    ),
                ],
            ),
        }
    )
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # получаем токен и закодированное id пользователя
        token = serializer.validated_data['token']
        encoded_id = serializer.validated_data['encoded_id']
        password = serializer.validated_data['password1']

        if verify_reset_password(token, encoded_id, password):
            # если успешно изменили пароль
            return Response({
                'detail': 'Пароль успешно изменен',
            }, status=status.HTTP_200_OK)
        else:
            # если возникла ошибка при подтверждении
            return Response({
                'detail': 'Возникла ошибка при подтверждении сброса пароля. Проверьте корректность ссылки',
            }, status=status.HTTP_400_BAD_REQUEST)
