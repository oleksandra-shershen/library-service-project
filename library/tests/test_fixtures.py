from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model

from borrowing.models import Borrowing
from library.models import Book
from payment.models import Payment


class FixturesTestCase(TestCase):
    fixtures = ["fixtures.json"]

    def test_user_count(self):
        """Checking the number of created users"""
        User = get_user_model()
        self.assertEqual(User.objects.count(), 10)

    def test_user_names(self):
        """Checking the names of created users"""
        users = get_user_model().objects.all()
        expected_names = [
            "John Doe",
            "Emily Johnson",
            "William Brown",
            "Sophia Martinez",
            "James Davis",
            "Olivia Garcia",
            "Ethan Wilson",
            "Isabella Lopez",
            "Logan Young",
            "Ava Hernandez",
        ]
        for user, expected_name in zip(users, expected_names):
            self.assertEqual(user.get_full_name(), expected_name)

    def test_book_count(self):
        """Checking the number of created books"""
        self.assertEqual(Book.objects.count(), 10)

    def test_book_titles(self):
        """Checking the titles of created books"""
        books = Book.objects.all()
        expected_titles = [
            "The Great Gatsby",
            "Pride and Prejudice",
            "The Catcher in the Rye",
            "Moby Dick",
            "The Hobbit",
            "Brave New World",
            "War and Peace",
            "The Alchemist",
            "Lord of the Flies",
            "The Road",
        ]
        for book, expected_title in zip(books, expected_titles):
            self.assertEqual(book.title, expected_title)

    def test_borrowing_count(self):
        """Checking the number of created records about book issuance"""
        self.assertEqual(Borrowing.objects.count(), 10)

    def test_borrowing_dates(self):
        """Checking the dates of issue and return of books"""
        borrowings = Borrowing.objects.all()
        for borrowing in borrowings:
            self.assertIsInstance(borrowing.borrow_date, date)
            self.assertIsInstance(borrowing.expected_return_date, date)
            if borrowing.actual_return_date is not None:
                self.assertIsInstance(borrowing.actual_return_date, date)

    def test_payment_count(self):
        """Checking the number of created payments"""
        self.assertEqual(Payment.objects.count(), 10)

    def test_payment_status(self):
        """Checking payment statuses"""
        payments = Payment.objects.all()
        for payment in payments:
            self.assertIn(payment.status, ["PAID", "UNPAID"])
