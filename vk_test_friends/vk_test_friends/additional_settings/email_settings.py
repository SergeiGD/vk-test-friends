import pathlib
from os import environ


SEND_EMAILS = environ.get('SEND_EMAILS', False)
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_HOST = environ.get('EMAIL_HOST')
EMAIL_HOST_USER = environ.get('EMAIL_USER')
DEFAULT_FROM_EMAIL = environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = environ.get('EMAIL_PASSWORD')
EMAIL_PORT = 465
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_MESSAGES_FILE = f'{pathlib.Path().resolve()}/email_messages.txt'
