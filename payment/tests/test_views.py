from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from library.models import Book
from borrowing.models import Borrowing
from payment.models import Payment

User = get_user_model()


class PaymentViewSetTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            email="admin@example.com", password="adminpass", is_staff=True
        )
        self.regular_user = User.objects.create_user(
            email="user@example.com", password="userpass"
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=2.99,
        )

        self.borrowing = Borrowing.objects.create(
            user=self.regular_user, book=self.book, expected_return_date="2024-07-01"
        )

        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            status="PENDING",
            payment_type="PAYMENT",
            session_url="https://example.com/",
            session_id="id_888",
            money_to_pay=15.00,
        )

        self.payment_url = reverse("payment:payment-list")

    def get_jwt_token(self, user):
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    def authenticate(self, user):
        token = self.get_jwt_token(user)
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + token)

    def test_admin_can_view_all_payments(self):
        self.authenticate(self.admin_user)
        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_regular_user_can_view_their_payments(self):
        self.authenticate(self.regular_user)
        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_regular_user_can_not_view_other_payments(self):
        another_user = User.objects.create_user(
            email="enouther_user@example.com", password="anotherpass"
        )
        another_borrowing = Borrowing.objects.create(
            user=another_user, book=self.book, expected_return_date="2024-07-01"
        )
        another_payment = Payment.objects.create(
            borrowing=another_borrowing,
            status="PENDING",
            payment_type="PAYMENT",
            session_url="https://example.com/",
            session_id="id_8889",
            money_to_pay=15.00,
        )
        self.authenticate(self.regular_user)
        response = self.client.get(self.payment_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_payment(self):
        self.authenticate(self.regular_user)
        data = {
            "borrowing": self.borrowing.id,
            "status": "PAID",
            "payment_type": "FINE",
            "session_url": "https://example.com/",
            "session_id": "id_1111",
            "money_to_pay": 15.00,
        }
        response = self.client.post(self.payment_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Payment.objects.count(), 2)

    def test_update_payment(self):
        self.authenticate(self.admin_user)
        payment_detail_url = reverse(
            "payment:payment-detail", kwargs={"pk": self.payment.id}
        )
        data = {
            "borrowing": self.borrowing.id,
            "status": "PAID",
            "payment_type": "PAYMENT",
            "session_url": self.payment.session_url,
            "session_id": self.payment.session_id,
            "money_to_pay": self.payment.money_to_pay,
        }
        response = self.client.put(payment_detail_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "PAID")
