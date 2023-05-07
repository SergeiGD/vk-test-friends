from django.utils import timezone

from users.models import CustomUser
from friend_requests.models import FriendRequest


def get_active_incoming_requests(user: CustomUser):
    """
    Получение активных входящих заявок пользователя
    :param user:
    :return:
    """
    return FriendRequest.objects.filter(
        target=user,
        date_confirmed=None,
        date_rejected=None,
    )


def get_active_outcoming_requests(user: CustomUser):
    """
    Получение активных исходящих заявок пользователя
    :param user:
    :return:
    """
    return FriendRequest.objects.filter(
        sender=user,
        date_confirmed=None,
        date_rejected=None,
    )


def confirm_request(request: FriendRequest):
    """
    Подтверждение входящей заявки
    :param request:
    :return:
    """
    # устанавливаем дату подтверждения
    request.date_confirmed = timezone.now()
    sender = request.sender
    target = request.target
    # добавляем в друзья
    target.friends.add(sender)
    request.save()


def reject_request(request: FriendRequest):
    """
    Отклонение входящей заявки
    :param request:
    :return:
    """
    # устанавливаем дату отклонения
    request.date_rejected = timezone.now()
    request.save()
    

def send_request(request: FriendRequest) -> bool:
    """
    Отправка (сохранение) заявки в друзья
    :param request:
    :return: булево значение создалась ли новая заявка
    """
    sender = request.sender
    target = request.target

    # ищем встречную заявку (когда получатель тоже отправил заявку отправителю)
    symmetric_request = get_active_incoming_requests(sender).filter(
        sender=target
    ).first()

    if symmetric_request is not None:
        # если нашли, то не сохраняем в БД новую заявку, а просто подтверждаем встречную
        confirm_request(symmetric_request)
        return False

    # иначе сохраняем заявку
    request.save()
    return True
