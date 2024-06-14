from django.utils import timezone
from django.urls import reverse
from library.models import Book
from rest_framework import status
from rest_framework.test import APITestCase

from user.models import User
from borrowing.models import Borrowing


class BorrowingFilterTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            first_name="John", last_name="Dee", email="user@gmail.com"
        )
        self.book = Book.objects.create(
            title="Sample Book",
            author="Sample Author",
            inventory=2,
            daily_fee=3,
        )

        now = timezone.now()
        self.borrowing1 = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=now + timezone.timedelta(days=7),
        )
        self.borrowing2 = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            expected_return_date=now + timezone.timedelta(days=14),
            actual_return_date=now + timezone.timedelta(days=10),
        )

        self.client.force_authenticate(user=self.user)

    def test_list_borrowings(self):
        url = reverse('borrowing:borrowing-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_user_id_as_staff(self):
        url = reverse('borrowing:borrowing-list') + '?user_id=' + str(self.user.id)
        staff_user = User.objects.create_user(
            first_name="Staff", last_name="User", email="staff@example.com", is_staff=True
        )
        self.client.force_authenticate(user=staff_user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_user_id_as_non_staff(self):
        url = reverse('borrowing:borrowing-list') + '?user_id=' + str(self.user.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_is_active_true(self):
        url = reverse('borrowing:borrowing-list') + '?is_active=true'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_by_is_active_false(self):
        url = reverse('borrowing:borrowing-list') + '?is_active=false'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_no_filter_params(self):
        url = reverse('borrowing:borrowing-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
