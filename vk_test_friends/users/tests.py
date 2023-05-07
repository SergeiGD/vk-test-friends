from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import CustomUser
from users.services import FriendshipStatuses
from friend_requests.models import FriendRequest


class UsersListTestCase(APITestCase):
    def test_users_list(self):
        """
        Тестирование получения списка пользователей
        :return:
        """
        response = self.client.get(reverse('users_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RetrieveUserTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='tester@gmai.com', password='qweqwe')

    def test_retrieve_user(self):
        """
        Тестирование получения пользователя
        :return:
        """
        response = self.client.get(reverse('user', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)


class FriendsListTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)
        response = self.client.post(reverse('token_get_pair'), {
            'email': 'tester@gmail.com',
            'password': 'qweqwe',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        self.friends = [
            CustomUser.objects.create(email='friend1@gmail.com', password='qweqwe', is_active=True),
            CustomUser.objects.create(email='friend2@gmail.com', password='qweqwe', is_active=True),
            CustomUser.objects.create(email='friend3@gmail.com', password='qweqwe', is_active=True),
        ]
        self.not_a_friends = CustomUser.objects.create(email='not_a_friend@gmail.com', password='qweqwe', is_active=True)
        self.user.friends.set(self.friends)

    def test_friends_list(self):
        """
        Тестирование получения списка друзей
        :return:
        """
        response = self.client.get(reverse('friends_list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)


class RetrieveDeleteFriendTestCase(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)
        response = self.client.post(reverse('token_get_pair'), {
            'email': 'tester@gmail.com',
            'password': 'qweqwe',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')

        self.friend = CustomUser.objects.create(email='friend@gmail.com', password='qweqwe', is_active=True)
        self.user.friends.add(self.friend)

        self.url = reverse('friend', kwargs={'pk': self.friend.pk})

    def test_retrieve_friend(self):
        """
        Тестирование получения друга
        :return:
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.friends.filter(pk=self.friend.pk).exists())
        self.assertEqual(response.data['id'], self.friend.pk)

    def test_delete_friend(self):
        """
        Тестирование удаления пользователя из списка друзей
        :return:
        """
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(self.user.friends.filter(pk=self.friend.pk).exists())


class FriendshipStatusTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(email='tester@gmail.com', password='qweqwe', is_active=True)
        cls.friend = CustomUser.objects.create(email='friend@gmail.com', password='qweqwe', is_active=True)
        cls.not_a_friend = CustomUser.objects.create(email='not_a_friend@gmail.com', password='qweqwe', is_active=True)
        cls.incoming_friend = CustomUser.objects.create(email='incoming@gmail.com', password='qweqwe', is_active=True)
        cls.outcoming_friend = CustomUser.objects.create(email='outcoming@gmail.com', password='qweqwe', is_active=True)

    def setUp(self) -> None:
        response = self.client.post(reverse('token_get_pair'), {
            'email': 'tester@gmail.com',
            'password': 'qweqwe',
        })
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {response.data["access"]}')
        self.user.friends.add(self.friend)
        FriendRequest.objects.create(sender=self.incoming_friend, target=self.user)
        FriendRequest.objects.create(sender=self.user, target=self.outcoming_friend)

    def test_get_friendship_status(self):
        """
        Тестирование получения статуса дружбы
        :return:
        """
        response_friends = self.client.get(reverse('friendship_status', kwargs={'pk': self.friend.pk}))
        self.assertEqual(response_friends.status_code, status.HTTP_200_OK)
        self.assertEqual(response_friends.data['status'], FriendshipStatuses.FRIENDS)

        response_no_request = self.client.get(reverse('friendship_status', kwargs={'pk': self.not_a_friend.pk}))
        self.assertEqual(response_no_request.status_code, status.HTTP_200_OK)
        self.assertEqual(response_no_request.data['status'], FriendshipStatuses.NO_REQUEST)

        response_incoming = self.client.get(reverse('friendship_status', kwargs={'pk': self.incoming_friend.pk}))
        self.assertEqual(response_incoming.status_code, status.HTTP_200_OK)
        self.assertEqual(response_incoming.data['status'], FriendshipStatuses.IN_REQUEST)

        response_outcoming = self.client.get(reverse('friendship_status', kwargs={'pk': self.outcoming_friend.pk}))
        self.assertEqual(response_outcoming.status_code, status.HTTP_200_OK)
        self.assertEqual(response_outcoming.data['status'], FriendshipStatuses.OUT_REQUEST)
