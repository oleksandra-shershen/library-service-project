from django.test import TestCase
from django.db.utils import IntegrityError, DataError
from django.core.exceptions import ValidationError
from library.models import Book


class BookModelTests(TestCase):

    def test_create_book(self):
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee="1.50",
        )
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(book.title, "Test Book")
        self.assertEqual(book.author, "Test Author")
        self.assertEqual(book.cover, "HARD")
        self.assertEqual(book.inventory, 10)
        self.assertEqual(book.daily_fee, "1.50")

    def test_str_representation(self):
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="HARD",
            inventory=10,
            daily_fee="1.50",
        )
        self.assertEqual(str(book), "Test Book")

    def test_default_author(self):
        book = Book.objects.create(
            title="Test Book", cover="HARD", inventory=10, daily_fee="1.50"
        )
        self.assertEqual(book.author, "Unknown Author")

    def test_invalid_cover_choice(self):
        with self.assertRaises(DataError):
            Book.objects.create(
                title="Test Book",
                author="Test Author",
                cover="INVALID",
                inventory=10,
                daily_fee="1.50",
            )

    def test_positive_inventory(self):
        with self.assertRaises(IntegrityError):
            Book.objects.create(
                title="Test Book",
                author="Test Author",
                cover="HARD",
                inventory=-1,
                daily_fee="1.50",
            )

    def test_decimal_daily_fee(self):
        with self.assertRaises(ValidationError):
            Book.objects.create(
                title="Test Book",
                author="Test Author",
                cover="HARD",
                inventory=10,
                daily_fee="invalid",
            )
