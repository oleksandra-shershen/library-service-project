from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from library.models import Book


class BookTest(APITestCase):
    def setUp(self):
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": "5",
            "daily_fee": 2.99
        }
        self.book = Book.objects.create(**self.book_data)

    def test_create_book(self):
        url = reverse("library:book-list")
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": "15",
            "daily_fee": 12.99
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(Book.objects.get(id=response.data["id"]).title, "New Book")

    def test_list_books(self):
        url = reverse("library:book-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_book(self):
        url = reverse("library:book-detail", kwargs={"pk": self.book.id})
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Book")

    def test_partial_update_book(self):
        url = reverse("library:book-detail", kwargs={"pk": self.book.id})
        data = {"title": "Update Book"}
        response = self.client.patch(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book.refresh_from_db()
        self.assertEqual(response.data["title"], "Update Book")

    def test_update_book(self):
        url = reverse("library:book-detail", kwargs={"pk": self.book.id})
        data = {
            "title": "Update Book",
            "author": "Update Author",
            "cover": "SOFT",
            "inventory": "1",
            "daily_fee": 3.49
        }
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Update Book")