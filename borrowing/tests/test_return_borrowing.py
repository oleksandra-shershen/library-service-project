from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from user.models import User
from library.models import Book
from borrowing.models import Borrowing


class BorrowingTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            first_name="John",
            last_name="Doe",
            email="user@example.com",
            password="password",
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            daily_fee=10.0,
            inventory=2,
        )

    def test_validation_errors(self):
        # Create a borrowing instance with invalid expected_return_date
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(
                user=self.user,
                book=self.book,
                borrow_date=timezone.now(),
                expected_return_date=timezone.now().date()
                - timezone.timedelta(days=1),
            )

        # Create a borrowing instance with invalid actual_return_date
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(
                user=self.user,
                book=self.book,
                borrow_date=timezone.now(),
                actual_return_date=timezone.now().date()
                - timezone.timedelta(days=1),
            )

        # Create a borrowing instance with book inventory less than 1
        self.book.inventory = 0
        self.book.save()
        with self.assertRaises(ValidationError):
            Borrowing.objects.create(
                user=self.user, book=self.book, borrow_date=timezone.now()
            )

    def test_valid_borrowing_creation(self):
        # Create a valid borrowing instance
        borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now(),
            expected_return_date=timezone.now().date()
            + timezone.timedelta(days=7),
        )
        self.assertEqual(borrowing.user, self.user)
        self.assertEqual(borrowing.book, self.book)
        self.assertIsNotNone(borrowing.borrow_date)
        self.assertEqual(
            borrowing.expected_return_date,
            timezone.now().date() + timezone.timedelta(days=7),
        )
