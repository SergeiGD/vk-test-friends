from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework.reverse import reverse

from users.models import CustomUser
from core.utils import send_email, EmailSubjects


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
    except(TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # если пользователь найден и токен верный, то подтверждаем аккаунт
        user.is_active = True
        user.save()
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
    except(TypeError, ValueError, OverflowError):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        # если пользователь найден и токен верный, то устанавливаем новый пароль
        user.set_password(password)
        user.save()
        return True
    return False
