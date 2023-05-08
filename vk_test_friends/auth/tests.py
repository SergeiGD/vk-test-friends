from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.core import mail

from core.utils import EmailSubjects
from .services import send_sing_up_email, send_reset_password_email
from users.models import CustomUser


class SingUpTestCase(APITestCase):
    def test_successful_sing_up(self):
        """
        Тестирование корректной регистрации
        :return:
        """
        response = self.client.post(reverse('sing_up'), {
            'email': 'tester@gmail.com',
            'password1': 'mypass123',
            'password2': 'mypass123',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(mail.outbox)
        self.assertEqual(mail.outbox[0].subject, EmailSubjects.VERIFY_ACCOUNT.value)

    def test_wrong_passwords_sing_up(self):
        """
        Тестирование регистрации с указанием разных паролей
        :return:
        """
        response = self.client.post(reverse('sing_up'), {
            'email': 'tester@gmail.com',
            'password1': 'mypass123',
            'password2': 'qweqwe',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class VerifyAccountTestCase(APITestCase):
    def setUp(self) -> None:
        user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=False)
        self.encoded_id, self.token = send_sing_up_email(user, 'localhost')

    def test_successful_verify_account(self):
        """
        Тестирование корректного подтверждения регистрации
        :return:
        """
        response = self.client.post(reverse('verify_account'), {
            'token': self.token,
            'encoded_id': self.encoded_id,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token_verify_account(self):
        """
        Тестирование подтверждения регистрации с неверным токеном
        :return:
        """
        response = self.client.post(reverse('verify_account'), {
            'token': 'wrong_token',
            'encoded_id': self.encoded_id,
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class RequestResetPasswordTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)

    def test_request_reset_password(self):
        """
        Тестирование запроса сброса пароля
        :return:
        """
        response = self.client.post(reverse('request_reset_password'), {
            'email': self.user.email,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(mail.outbox)
        self.assertEqual(mail.outbox[0].subject, EmailSubjects.RESET_PASSWORD.value)


class ConfirmResetTestCase(APITestCase):
    def setUp(self) -> None:
        self.user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)
        self.encoded_id, self.token = send_reset_password_email(self.user, 'localhost')

    def test_successful_reset_password(self):
        """
        Тестирование корректного сброса пароля
        :return:
        """
        response = self.client.post(reverse('confirm_reset_password'), {
            'token': self.token,
            'encoded_id': self.encoded_id,
            'password1': 'mypass123',
            'password2': 'mypass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token_reset_password(self):
        """
        Тестирование сброса пароля с неверным токеном
        :return:
        """
        response = self.client.post(reverse('confirm_reset_password'), {
            'token': 'wrong_token',
            'encoded_id': self.encoded_id,
            'password1': 'mypass123',
            'password2': 'mypass123',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_wrong_passwords_reset_password(self):
        """
        Тестирование сброса пароля с указанием разных паролей
        :return:
        """
        response = self.client.post(reverse('confirm_reset_password'), {
            'token': 'wrong_token',
            'encoded_id': self.encoded_id,
            'password1': 'mypass123',
            'password2': 'qweqwe',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
