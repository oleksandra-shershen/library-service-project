from django.test import TestCase
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from rest_framework.exceptions import ValidationError
from library.models import Book
from borrowing.models import Borrowing


class BorrowingModelTests(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="testuser@test.com",
            password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=5,
            daily_fee="1.50"
        )

    def test_create_borrowing(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=10),
            book=self.book,
            user=self.user
        )
        self.assertEqual(Borrowing.objects.count(), 1)
        self.assertEqual(borrowing.book, self.book)
        self.assertEqual(borrowing.user, self.user)

    def test_expected_return_date_before_borrow_date(self):
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(
                expected_return_date=date.today() - timedelta(days=1),
                book=self.book,
                user=self.user
            )

    def test_actual_return_date_before_borrow_date(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=10),
            book=self.book,
            user=self.user
        )
        borrowing.actual_return_date = date.today() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            borrowing.save()

    def test_book_not_available_for_borrowing(self):
        self.book.inventory = 0
        self.book.save()
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(
                expected_return_date=date.today() + timedelta(days=10),
                book=self.book,
                user=self.user
            )

    def test_return_borrowing(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=10),
            book=self.book,
            user=self.user
        )
        borrowing.return_borrowing()
        self.assertIsNotNone(borrowing.actual_return_date)
        self.assertEqual(self.book.inventory, 6)

    def test_return_borrowing_already_returned(self):
        borrowing = Borrowing.objects.create(
            expected_return_date=date.today() + timedelta(days=10),
            book=self.book,
            user=self.user
        )
        borrowing.return_borrowing()
        with self.assertRaises(ValidationError):
            borrowing.return_borrowing()
