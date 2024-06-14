import datetime

from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken

from library.models import Book
from borrowing.models import Borrowing

User = get_user_model()


class BorrowingViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(email='user@example.com', password='password')
        self.admin_user = User.objects.create_superuser(email='admin@example.com', password='password')

        self.book = Book.objects.create(title='Test Book', author='Test Author')

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=datetime.date.today() + datetime.timedelta(days=7)
        )

        self.user_token = RefreshToken.for_user(self.user).access_token
        self.admin_token = RefreshToken.for_user(self.admin_user).access_token

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.user_token))

    def test_create_borrowing(self):
        url = reverse('borrowing-list')
        data = {
            'expected_return_date': (datetime.date.today() + datetime.timedelta(days=10)).isoformat(),
            'book': self.book.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Borrowing.objects.count(), 2)
        self.assertEqual(Borrowing.objects.last().user, self.user)

    def test_list_borrowings(self):
        url = reverse('borrowing-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_borrowing(self):
        url = reverse('borrowing-detail', kwargs={'pk': self.borrowing.pk})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['book'], self.book.id)

    def test_filter_borrowings_by_is_active(self):
        url = reverse('borrowing-list')

        response = self.client.get(url, {'is_active': 'true'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        self.borrowing.actual_return_date = datetime.date.today()
        self.borrowing.save()

        response = self.client.get(url, {'is_active': 'false'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_see_all_borrowings(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.admin_token))
        url = reverse('borrowing-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_filter_borrowings_by_user_id(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(self.admin_token))
        url = reverse('borrowing-list')
        response = self.client.get(url, {'user_id': self.user.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_non_authenticated_user_cannot_access_borrowings(self):
        self.client.credentials()
        url = reverse('borrowing-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
