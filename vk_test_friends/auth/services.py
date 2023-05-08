from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.reverse import reverse
import logging

from users.models import CustomUser
from core.utils import send_email, EmailSubjects

logger = logging.getLogger('auth_logger')



class SingUpTokenGenerator(PasswordResetTokenGenerator):
    """
    Класс для генерации токена для регистрации
    """
    def _make_hash_value(self, user, timestamp):
        """
        Переопределенный make_hash_value, чтоб он использовал is_active и после активации становился невалидным
        :param user:
        :param timestamp:
        :return:
        """
        return f"{user.pk}{timestamp}{user.is_active}"


def sing_up_user(sing_up_data: dict):
    """
    Регистрация пользователя
    :param sing_up_data: словарь с данными регистрации
    :return:
    """
    # преобразуем данные в удобный вид и поставим значения по умолчанию (is_active, is_staff, is_superuser)
    user_data = {
        'email': sing_up_data['email'],
        'password': sing_up_data['password1'],
        'first_name': sing_up_data.get('first_name', ''),
        'last_name': sing_up_data.get('last_name', ''),
        'is_staff': False,
        'is_active': False,
        'is_superuser': False,
    }
    user = CustomUser.objects.filter(email=user_data['email'], is_active=False).first()
    if user is not None:
        logger.info(f'аккаунт {user.email} уже зарегистрирован, но не подтвержден,обновление информации')
        # если пользователь уже регистрировался, но так и не подтвердил аккаунт, то просто обновим данные
        user.first_name = user_data['first_name']
        user.last_name = user_data['last_name']
        user.save()
        user.set_password(user_data['password'])
        return user
    logger.info(f'аккаунт {user_data["email"]} создан, ожидание подтверждения')
    return CustomUser.objects.create_user(**user_data)


def send_sing_up_email(user: CustomUser, domain: str):
    """
    Отправка письма для подтверждения регистрации
    :param user: пользователь
    :param domain: домен сайта
    :return:
    """
    # создаем экземпляр генератора токенов подтверждения регистрации
    account_activation_token = SingUpTokenGenerator()

    # кодируем id пользователя
    encoded_id = urlsafe_base64_encode(force_bytes(user.pk))
    # генерируем токен
    token = account_activation_token.make_token(user)
    # строим ссылку для подтверждения
    relative_url = reverse('verify_account')
    absolute_url = f'http://{domain}{relative_url}?id={encoded_id}&token={token}'

    # создаем тему и тело письма
    email_subject = EmailSubjects.VERIFY_ACCOUNT.value
    email_content = f'Добрый день! Для подтверждения регистрации перейдите по следующей ссылке: {absolute_url}'

    # отправляем письмо
    send_email(subject=email_subject, content=email_content, send_to=user.email)

    # вернем id и токен
    return encoded_id, token


def verify_account(token: str, encoded_id: str) -> bool:
    """
    Подтверждение аккаунита
    :param token: токен подтверждения
    :param encoded_id: закодированный id пользователя
    :return: булево значение успеха
    """
    account_activation_token = SingUpTokenGenerator()
    try:
        # пытаемся получить id пользователя из закодированного id
        user_id = force_str(urlsafe_base64_decode(encoded_id))
        # пытаемся получить пользователя с таким id
        user = CustomUser.objects.filter(pk=user_id).first()
    except(TypeError, ValueError, OverflowError) as err:
        logger.warning(f'ошибка подтверждения аккаунта. {str(err)}')
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # если пользователь найден и токен верный, то подтверждаем аккаунт
        user.is_active = True
        user.save()
        logger.info(f'аккаунт {user.email} успешно подтвержден')
        return True
    return False


def send_reset_password_email(user: CustomUser, domain: str):
    """
    Запрос сброса пароля
    :param user: пользователь, которому нужно сбросить пароль
    :param domain: домен сайта
    :return:
    """
    # создаем экземпляр генератора токенов сброса пароля
    reset_password_token = PasswordResetTokenGenerator()

    # кодируем id пользователя
    encoded_id = urlsafe_base64_encode(force_bytes(user.pk))
    # генерируем токен
    token = reset_password_token.make_token(user)
    # строим ссылку для подтверждения
    relative_url = reverse('confirm_reset_password')
    absolute_url = f'http://{domain}{relative_url}?id={encoded_id}&token={token}'

    # создаем тему и тело письма
    email_subject = EmailSubjects.RESET_PASSWORD.value
    email_content = f'Добрый день! Для сброса пароля перейдите по следующей ссылке: {absolute_url}'

    # отправляем письмо
    send_email(subject=email_subject, content=email_content, send_to=user.email)
    logger.info(f'запрошен сброс пароля для {user.email}')

    # вернем id и токен
    return encoded_id, token


def verify_reset_password(token: str, encoded_id: str, password: str) -> bool:
    """
    Подтверждение сброса пароля
    :param token: токен подтверждения
    :param encoded_id: закодированный id пользователя
    :param password: новый пароль пользователя
    :return: булево значение успеха
    """
    account_activation_token = PasswordResetTokenGenerator()
    try:
        # пытаемся получить id пользователя из закодированного id
        user_id = force_str(urlsafe_base64_decode(encoded_id))
        # пытаемся получить пользователя с таким id
        user = CustomUser.objects.filter(pk=user_id).first()
    except(TypeError, ValueError, OverflowError) as err:
        logger.warning(f'ошибка подтверждения сброса пароля. {str(err)}')
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # если пользователь найден и токен верный, то устанавливаем новый пароль
        user.set_password(password)
        user.save()
        logger.info(f'успешно сброшен пароль для {user.email}')
        return True
    return False
