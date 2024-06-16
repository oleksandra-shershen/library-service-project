from django.db import models

from borrowing.models import Borrowing


class Payment(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
    ]

    TYPE_CHOICES = [
        ("PAYMENT", "Payment"),
        ("FINE", "Fine"),
    ]

    status = models.CharField(
        max_length=7, choices=STATUS_CHOICES, default="PENDING"
    )
    payment_type = models.CharField(
        max_length=7, choices=TYPE_CHOICES, default="PAYMENT"
    )
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.CASCADE, related_name="payments"
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=255)
    money_to_pay = models.DecimalField(decimal_places=2, max_digits=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.borrowing.book.title} - {self.get_status_display()}"
