from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

from borrowing.models import Borrowing
from library.models import Book
from payment.models import Payment


User = get_user_model()


class PaymentViewSetTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@admin.com",
            password="adminpass",
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email="regular_user@user.com",
            password="userpass",
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=4,
            daily_fee=2.99
        )

        self.borrowing = Borrowing.objects.create(
            user=self.admin_user,
            book=self.book,
            expected_return_date="2024-07-01"
        )

        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            status="PENDING",
            type="PAYMENT",
            session_url="https://example.com/",
            session_id="id_888",
            money_to_pay=15.00,
        )

        self.payment_url = reverse("payment-list")