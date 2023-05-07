from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, ListCreateAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .serializers import IncomingRequestsSerializer, OutcomingRequestsSerializer
from friend_requests.models import FriendRequest
from .services import (
    get_active_incoming_requests, get_active_outcoming_requests, send_request, confirm_request, reject_request,
)


class OutcomingRequestsListAPiView(ListCreateAPIView):
    """
    Получение списка исходящих заявок и отправки новых
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = OutcomingRequestsSerializer

    def get_queryset(self):
        # переопределим get_queryset, что возвращал заявки текущего пользователя
        return get_active_outcoming_requests(self.request.user)

    @extend_schema(
        responses={
            '204': OpenApiResponse(
                description='Подтверждена встречная заявка',
            ),
            '201': OpenApiResponse(
                description='Заявка отправлена',
                response=OutcomingRequestsSerializer,
            )
        },
    )
    def post(self, request, *args, **kwargs):
        # фиксируем пользователя (отправителя)
        sender = self.request.user
        # в контекст сериалайзера добавим отправителя
        serializer = self.get_serializer(data=request.data, context={'sender': sender})
        # производим валидацию
        serializer.is_valid(raise_exception=True)
        # не используем сериалайзер для сохранения, т.к. не всегда создаем заявку (если есть встречная заявка)
        request = FriendRequest(**serializer.validated_data)
        request.sender = sender
        if send_request(request):
            # если вернулось True, то значит заявка создана
            data = self.get_serializer(request).data
            return Response(data, status=status.HTTP_201_CREATED)
        # иначе была встречная заявка и новую мы не создавали, а просто подтвердили встречную
        return Response(status=status.HTTP_204_NO_CONTENT)


class IncomingRequestsListAPiView(ListAPIView):
    """
    Получение списка входящих заявок
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = IncomingRequestsSerializer

    def get_queryset(self):
        # переопределим get_queryset, что возвращал заявки текущего пользователя
        return get_active_incoming_requests(self.request.user)


class IncomingRequestAPiView(RetrieveAPIView):
    """
    Просмотр входящей заявки
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = IncomingRequestsSerializer

    def get_queryset(self):
        # переопределим get_queryset, что возвращал заявки текущего пользователя
        return get_active_incoming_requests(self.request.user)


class OutcomingRequestAPiView(RetrieveDestroyAPIView):
    """
    Просмотр и удаление исходящей заявки
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = OutcomingRequestsSerializer

    def get_queryset(self):
        # переопределим get_queryset, что возвращал заявки текущего пользователя
        return get_active_outcoming_requests(self.request.user)


@extend_schema(
    request=None,
    description='Подтверждение заявки в друзья',
    responses={
        '200': OpenApiResponse(
            description='Успешное подтверждение',
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    'Успешное подтверждение',
                    value={
                        'detail': 'Заявка в друзья принята',
                    },
                ),
            ],
        ),
    },
)
@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def confirm_request_api_view(request, pk):
    """
    Подтверждения входящей заявки
    :param request:
    :param pk:
    :return:
    """
    # ищем активную входящую заявку пользователя с указанным id
    request = get_active_incoming_requests(request.user).filter(pk=pk).first()
    if request is None:
        return Response({
            'detail': 'Заявка не найдена',
        }, status=status.HTTP_404_NOT_FOUND)

    # подтверждаем заявку
    confirm_request(request)
    return Response({
        'detail': 'Заявка в друзья принята',
    }, status=status.HTTP_200_OK)


@extend_schema(
    request=None,
    description='Отклонения входящей заявки',
    responses={
        '200': OpenApiResponse(
            description='Успешное отклонение',
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    'Успешное отклонение',
                    value={
                        'detail': 'Заявка в друзья отклонена',
                    },
                ),
            ],
        ),
    },
)
@api_view(['POST', ])
@permission_classes([IsAuthenticated, ])
def reject_request_api_view(request, pk):
    """
    Отклонения входящей заявки
    :param request:
    :param pk:
    :return:
    """
    # ищем активную входящую заявку пользователя с указанным id
    request = get_active_incoming_requests(request.user).filter(pk=pk).first()
    if request is None:
        return Response({
            'detail': 'Заявка не найдена',
        }, status=status.HTTP_404_NOT_FOUND)

    # отклоняем заявку
    reject_request(request)
    return Response({
        'detail': 'Заявка в друзья отклонена',
    }, status=status.HTTP_200_OK)
