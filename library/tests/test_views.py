from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from user.models import User
from library.models import Book


class BookTest(APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create_user(
            first_name="admin",
            last_name="admin",
            password="adminpass",
            email="admin@gmail.com",
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            first_name="user",
            last_name="user",
            password="userpass",
            email="user@gmail.com",
            is_staff=False,
        )
        self.book_data = {
            "title": "Test Book",
            "author": "Test Author",
            "cover": "HARD",
            "inventory": "5",
            "daily_fee": 2.99,
        }
        self.book = Book.objects.create(**self.book_data)

        self.admin_token = self.get_tokens_for_user(self.admin_user)
        self.regular_token = self.get_tokens_for_user(self.regular_user)

    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

    def test_create_book_admin_user(self):
        url = reverse("library:book-list")
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": "15",
            "daily_fee": 12.99,
        }
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token["access"]}'
        )
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)
        self.assertEqual(
            Book.objects.get(id=response.data["id"]).title, "New Book"
        )

    def test_create_book_authenticated_user(self):
        url = reverse("library:book-list")
        data = {
            "title": "New Book",
            "author": "New Author",
            "cover": "SOFT",
            "inventory": "15",
            "daily_fee": 12.99,
        }
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.regular_token["access"]}'
        )
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_books(self):
        url = reverse("library:book-list")
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token["access"]}'
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_get_book(self):
        url = reverse("library:book-detail", kwargs={"pk": self.book.id})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token["access"]}'
        )
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Test Book")

    def test_partial_update_book(self):
        url = reverse("library:book-detail", kwargs={"pk": self.book.id})
        data = {"title": "Update Book"}
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token["access"]}'
        )
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
            "daily_fee": 3.49,
        }
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token["access"]}'
        )
        response = self.client.put(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Update Book")

    def test_delete_book(self):
        url = reverse("library:book-detail", kwargs={"pk": self.book.id})
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {self.admin_token["access"]}'
        )
        response = self.client.delete(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)
