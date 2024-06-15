from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from library.models import Book
from user.models import User
from borrowing.models import Borrowing


class FinePaymentTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            first_name="John", last_name="Doe", email="user@example.com"
        )
        self.book = Book.objects.create(
            title="Sample Book",
            author="Sample Author",
            inventory=2,
            daily_fee=3,
        )
        now = timezone.now().date()

        # Create a borrowing with expected_return_date in the future (valid)
        self.borrowing_future = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=now - timezone.timedelta(days=5),  # Borrowed 5 days ago
            expected_return_date=now + timezone.timedelta(days=3),  # Expected return in 3 days
        )

        # Create another borrowing with expected_return_date also in the future (valid)
        self.borrowing_future2 = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=now - timezone.timedelta(days=10),  # Borrowed 10 days ago
            expected_return_date=now + timezone.timedelta(days=5),  # Expected return in 5 days
        )

    def test_return_borrowing_overdue_with_fine(self):
        url = reverse("borrowing:return", kwargs={"pk": self.borrowing_future.pk})
        data = {"actual_return_date": timezone.now().date()}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("fine", response.data.lower())

    def test_return_borrowing_not_overdue_no_fine(self):
        url = reverse("borrowing:return", kwargs={"pk": self.borrowing_future2.pk})
        data = {"actual_return_date": timezone.now().date()}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("fine", response.data.lower())
