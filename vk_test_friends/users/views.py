from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView, get_object_or_404, RetrieveAPIView, RetrieveDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample

from .serializers import UsersSerializer
from .services import get_friends_list, get_friendship_status, remove_from_friends_list, FriendshipStatuses
from .models import CustomUser


class UsersListAPIView(ListAPIView):
    """
    Получение списка пользователей
    """
    serializer_class = UsersSerializer
    queryset = CustomUser.objects.all()


class UserAPIView(RetrieveAPIView):
    """
    Получение информации о пользователе
    """
    serializer_class = UsersSerializer
    queryset = CustomUser.objects.all()


class FiendsListAPIView(ListAPIView):
    """
    Получение списка друзей
    """
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        # переопределим get_queryset, что возвращал список друзей текущего пользователя
        return get_friends_list(self.request.user)


class FriendAPIView(RetrieveDestroyAPIView):
    """
    Получение информации о друге и удаления его из списка друзей
    """
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated, )

    def get_queryset(self):
        # переопределим get_queryset, что возвращал список друзей текущего пользователя
        return get_friends_list(self.request.user)


    def perform_destroy(self, instance):
        # переопределим perform_destroy, чтоб просто удалять из списка друзей
        remove_from_friends_list(self.request.user, self.get_object())


@extend_schema(
    request=None,
    description='Получение статуса дружбы с пользователем',
    responses={
        '200': OpenApiResponse(
            description='Статус получен',
            response=OpenApiTypes.OBJECT,
            examples=[
                OpenApiExample(
                    'Статус друзья',
                    value={
                        'status': FriendshipStatuses.FRIENDS.value,
                    },
                ),
                OpenApiExample(
                    'Статус есть входящая заявка',
                    value={
                        'status': FriendshipStatuses.IN_REQUEST.value,
                    },
                ),
            ],
        ),
    }
)
@api_view(['GET', ])
@permission_classes([IsAuthenticated, ])
def friendship_status_api_view(request, pk):
    """
    Вью получение статута дружбы
    :param request:
    :param pk:
    :return:
    """
    target = get_object_or_404(CustomUser, pk=pk)

    return Response({
        'status': get_friendship_status(request.user, target),
    }, status=status.HTTP_200_OK)
