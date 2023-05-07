from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    """
    Модель пользователя
    """

    email = models.EmailField(
        verbose_name='Эл. почта',
        unique=True,
    )

    friends = models.ManyToManyField(
        to='self',
        verbose_name='Друзья',
    )

    date_created = models.DateTimeField(
        verbose_name='Дата создания',
        blank=True,
        null=True,
        default=timezone.now,
    )

    # будет производить аутентификацию по эл. почте, так что стандартный username не нужен
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    # установим менеджер для создания пользователей по эл. почте
    objects = CustomUserManager()
