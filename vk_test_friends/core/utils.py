from enum import Enum
from django.core.mail import EmailMessage
from django.conf import settings
from datetime import datetime
from smtplib import SMTPException
import logging

email_logger = logging.getLogger('email_logger')


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
    email_logger.info(f'Отправка письма пользователю {send_to} Тема - {subject}')
    if settings.DEBUG:
        # если DEBUG, то для удобства запишем в файл, чтоб не лазить на почту
        with open(settings.EMAIL_MESSAGES_FILE, 'a') as f:
            f.write(f'{send_to} - {datetime.now()} - {subject} - {content} \n')

    if settings.SEND_EMAILS:
        # если в настройках указано не отправлять письма, то только отправка производится не будет
        email = EmailMessage(
            subject=subject,
            body=content,
            to=[send_to, ],
        )
        try:
            email.send()
            email_logger.info(f'Письмо для пользователя {send_to} отправлено')
        except SMTPException as err:
            email_logger.error(f'Ошибка отправки письма! {str(err)}')
    else:
        email_logger.warning(
            'Отправка писем отключена. Если включен режим отладки, письмо будет доступно в файле email_messages.txt'
        )
