from users.models import CustomUser
from enum import Enum

from friend_requests.services import get_active_incoming_requests, get_active_outcoming_requests


class FriendshipStatuses(str, Enum):
    """
    Enum для статутов дружбы
    """
    FRIENDS = 'Друзья'
    NO_REQUEST = 'Нет активной заявки'
    IN_REQUEST = 'Есть входящая заявка'
    OUT_REQUEST = 'Есть исходящая заявка'


def get_friends_list(user: CustomUser):
    """
    Получение списка друзей пользователя
    :param user:
    :return:
    """
    return user.friends.all()


def get_friendship_status(user: CustomUser, target: CustomUser):
    """
    Получение статуса дружбы пользователей
    :param user: первый пользователь
    :param target: второй пользователь
    :return:
    """
    if CustomUser.objects.filter(
        friends__pk=target.id, pk=user.pk,
    ).exists():
        return FriendshipStatuses.FRIENDS
    if get_active_incoming_requests(user).filter(sender=target):
        return FriendshipStatuses.IN_REQUEST
    if get_active_outcoming_requests(user).filter(target=target):
        return FriendshipStatuses.OUT_REQUEST
    return FriendshipStatuses.NO_REQUEST


def remove_from_friends_list(user: CustomUser, target: CustomUser):
    """
    Удаление пользователя из списка друзей
    :param user: первый пользователь
    :param target: второй пользователь
    :return:
    """
    user.friends.remove(target)
