from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Borrowing
from .views import BorrowingViewSet
from payment.models import Payment

class BorrowingViewSetTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.borrowing = Borrowing.objects.create(
            expected_return_date="2024-06-15",
            actual_return_date=None,
            book_id=1,  # Предполагая, что у вас есть модель Book с id=1
            user_id=1,  # Предполагая, что у вас есть пользователь с id=1
        )

    def test_return_borrowing_with_fine(self):
        url = reverse('borrowing:return', kwargs={'pk': self.borrowing.pk})
        data = {"actual_return_date": "2024-06-17"}  # Задержка возврата
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("fine", response.data["message"].lower())

    def test_create_fine_payment(self):
        fine_amount = 10.0  # Уточните сумму штрафа в соответствии с вашими расчетами
        create_fine_payment(self.borrowing, fine_amount)
        payment = Payment.objects.filter(borrowing=self.borrowing).first()
        self.assertEqual(payment.money_to_pay, fine_amount)
        self.assertEqual(payment.payment_type, 'FINE')
