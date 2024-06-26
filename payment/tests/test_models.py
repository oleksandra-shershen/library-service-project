from django.contrib.auth import get_user_model
from django.test import TestCase
from library.models import Book
from borrowing.models import Borrowing
from payment.models import Payment

User = get_user_model()


class PaymentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="testpassword",
        )

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee=2.99,
        )

        self.borrowing = Borrowing.objects.create(
            user=self.user, book=self.book, expected_return_date="2024-07-01"
        )

        self.payment = Payment.objects.create(
            borrowing=self.borrowing,
            status="PENDING",
            payment_type="PAYMENT",
            session_url="https://example.com/",
            session_id="id_888",
            money_to_pay=15.00,
        )

    def test_payment_creation(self):
        self.assertEqual(self.payment.borrowing, self.borrowing)
        self.assertEqual(self.payment.status, "PENDING")
        self.assertEqual(self.payment.payment_type, "PAYMENT")
        self.assertEqual(self.payment.session_url, "https://example.com/")
        self.assertEqual(self.payment.session_id, "id_888")
        self.assertEqual(self.payment.money_to_pay, 15.00)
        self.assertIsNotNone(self.payment.created_at)
        self.assertIsNotNone(self.payment.updated_at)

    def test_payment_str(self):
        expected_str = f"{self.borrowing.book.title} - {self.payment.get_status_display()}"
        self.assertEqual(str(self.payment), expected_str)

    def test_payment_status_choices(self):
        payment = Payment.objects.get(id=self.payment.id)
        self.assertIn(payment.status, dict(Payment.STATUS_CHOICES))

    def test_payment_type_choices(self):
        payment = Payment.objects.get(id=self.payment.id)
        self.assertIn(payment.payment_type, dict(Payment.TYPE_CHOICES))
