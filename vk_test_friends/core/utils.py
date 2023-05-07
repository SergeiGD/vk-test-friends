from enum import Enum
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime


class EmailSubjects(str, Enum):
    """
    Enum для статутов дружбы
    """
    VERIFY_ACCOUNT = 'Подтверждение регистрации'
    RESET_PASSWORD = 'Сброс пароля'


def send_email(subject: str, content: str, send_to: str):
    """
    Отправка писем
    :param subject: тема письма
    :param content: контент письма
    :param send_to: получатель
    :return:
    """
    email = EmailMessage(
        subject=subject,
        body=content,
        to=[send_to],
    )

    if settings.DEBUG:
        # если DEBUG, то для удобства запишем в файл, чтоб не лазить на почту
        with open(settings.EMAIL_MESSAGES_FILE, 'a') as f:
            f.write(f'{send_to} - {datetime.now()} - {subject} - {content} \n')

    email.send()
