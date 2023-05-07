from django.db import models
from django.utils import timezone

from users.models import CustomUser


class FriendRequest(models.Model):
    """
    Модель запроса добавления в друзья
    """

    sender = models.ForeignKey(
        to=CustomUser,
        verbose_name='Отправитель',
        related_name='outcoming_requests',
        related_query_name='outcoming_request',
        on_delete=models.CASCADE,
    )

    target = models.ForeignKey(
        to=CustomUser,
        verbose_name='Адресат',
        related_name='incoming_requests',
        related_query_name='incoming_request',
        on_delete=models.CASCADE,
    )

    date_created = models.DateTimeField(
        verbose_name='Дата создания',
        blank=True,
        null=True,
        default=timezone.now,
    )

    date_confirmed = models.DateTimeField(
        verbose_name='Дата принятия',
        blank=True,
        null=True,
    )

    date_rejected = models.DateTimeField(
        verbose_name='Дата отклонения',
        blank=True,
        null=True,
    )
