from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from users.models import CustomUser
from friend_requests.models import FriendRequest


class IncomingRequestsListTestCase(APITestCase):
    def setUp(self):
        CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)
        response = self.client.post(reverse('token_get_pair'), {
            'email': 'tester@gmail.com',
            'password': 'qweqwe',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

    def test_incoming_requests_list(self):
        """
        Тестирование получения списка входящих заявок
        :return:
        """
        response = self.client.get(reverse('incoming_requests_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RetrieveIncomingRequestTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)
        response = self.client.post(reverse('token_get_pair'), {
            'email': 'tester@gmail.com',
            'password': 'qweqwe',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        self.sender = CustomUser.objects.create(email='incoming@gmail.com', password='qweqwe', is_active=True)
        self.incoming_request = FriendRequest.objects.create(sender=self.sender, target=self.user)

    def test_retrieve_incoming_request(self):
        """
        Тестирование получения входящей заявки
        :return:
        """
        response = self.client.get(reverse('incoming_request', kwargs={'pk': self.incoming_request.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.incoming_request.pk)


class ConfirmRequestTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)
        response = self.client.post(reverse('token_get_pair'), {
            'email': 'tester@gmail.com',
            'password': 'qweqwe',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        self.sender = CustomUser.objects.create(email='incoming@gmail.com', password='qweqwe', is_active=True)
        self.incoming_request = FriendRequest.objects.create(sender=self.sender, target=self.user)

    def test_confirm_request(self):
        """
        Тестирование принятия заявки
        :return:
        """
        response = self.client.post(reverse('confirm_request', kwargs={'pk': self.incoming_request.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.sender, self.user.friends.all())
        self.incoming_request.refresh_from_db()
        self.assertIsNotNone(self.incoming_request.date_confirmed)
        self.assertIsNone(self.incoming_request.date_rejected)


class RejectRequestTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)
        response = self.client.post(reverse('token_get_pair'), {
            'email': 'tester@gmail.com',
            'password': 'qweqwe',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        self.sender = CustomUser.objects.create(email='incoming@gmail.com', password='qweqwe', is_active=True)
        self.incoming_request = FriendRequest.objects.create(sender=self.sender, target=self.user)

    def test_reject_request(self):
        """
        Тестирование отклонения заявки
        :return:
        """
        response = self.client.post(reverse('reject_request', kwargs={'pk': self.incoming_request.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn(self.sender, self.user.friends.all())
        self.incoming_request.refresh_from_db()
        self.assertIsNotNone(self.incoming_request.date_rejected)
        self.assertIsNone(self.incoming_request.date_confirmed)


class ListCreateOutcomingRequestsTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)
        response = self.client.post(reverse('token_get_pair'), {
            'email': 'tester@gmail.com',
            'password': 'qweqwe',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

    def test_outcoming_requests_list(self):
        """
        Тестирование получения списка исходящих заявок
        :return:
        """
        response = self.client.get(reverse('outcoming_requests_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_correct_outcoming_request(self):
        """
        Корректная создания заявки
        :return:
        """
        target = CustomUser.objects.create(email='target@gmail.com', password='qweqwe', is_active=True)
        outcoming_request_data = {
            'target': target.id,
        }
        response = self.client.post(reverse('outcoming_requests_list'), outcoming_request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_duplicated_outcoming_request(self):
        """
        Тестирования создания дублирующей заявки (когда уже есть активная)
        :return:
        """
        target = CustomUser.objects.create(email='incoming@gmail.com', password='qweqwe', is_active=True)
        outcoming_request_data = {
            'target': target.id,
        }
        response = self.client.post(reverse('outcoming_requests_list'), outcoming_request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(reverse('outcoming_requests_list'), outcoming_request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_self_outcoming_request(self):
        """
        Тестирования создания заявки самому себе
        :return:
        """
        outcoming_request_data = {
            'target': self.user.id,
        }
        response = self.client.post(reverse('outcoming_requests_list'), outcoming_request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_friends_outcoming_request(self):
        """
        Тестирования создания заявки пользователю, с котором уже друзья
        :return:
        """
        target = CustomUser.objects.create(email='incoming@gmail.com', password='qweqwe', is_active=True)
        self.user.friends.add(target)
        outcoming_request_data = {
            'target': target.id,
        }
        response = self.client.post(reverse('outcoming_requests_list'), outcoming_request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_symmetric_outcoming_request(self):
        """
        Тестирования создания встречной заявки
        :return:
        """
        target = CustomUser.objects.create(email='incoming@gmail.com', password='qweqwe', is_active=True)
        FriendRequest.objects.create(sender=target, target=self.user)
        outcoming_request_data = {
            'target': target.id,
        }
        response = self.client.post(reverse('outcoming_requests_list'), outcoming_request_data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class RetrieveDeleteOutcomingRequestTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)
        response = self.client.post(reverse('token_get_pair'), {
            'email': 'tester@gmail.com',
            'password': 'qweqwe',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        target = CustomUser.objects.create(email='target@gmail.com', password='qweqwe', is_active=True)

        self.outcoming_reqeust = FriendRequest.objects.create(sender=self.user, target=target)

        self.url = reverse('outcoming_request', kwargs={'pk': self.outcoming_reqeust.pk})

    def test_retrieve_outcoming_reqeust(self):
        """
        Тестирование получения исходящей заявки
        :return:
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.outcoming_reqeust.pk)

    def test_delete_outcoming_reqeust(self):
        """
        Тестирование удаления исходящей заявки
        :return:
        """
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
