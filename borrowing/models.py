from django.db import models
from rest_framework.exceptions import ValidationError

from django.apps import apps
from library.models import Book
from library_service import settings

FINE_MULTIPLIER = 2


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="borrowings",
    )

    def __str__(self) -> str:
        return (
            f"Book: {self.book.title}, Author: {self.book.author}. "
            f"Borrowed from {self.borrow_date} to {self.expected_return_date}."
        )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(
                    expected_return_date__gte=models.F("borrow_date")
                ),
                name="expected_return_date_gte_borrow_date",
            ),
            models.CheckConstraint(
                check=models.Q(
                    actual_return_date__gte=models.F("borrow_date")
                ),
                name="actual_return_date_gte_borrow_date",
            ),
        ]

    def return_borrowing(self):
        if self.actual_return_date is None:
            raise ValidationError("Actual return date is not set.")
        self.book.inventory += 1
        self.book.save()
        self.save()

        if self.actual_return_date > self.expected_return_date:
            overdue_days = (self.actual_return_date - self.expected_return_date).days
            fine_amount = overdue_days * self.book.daily_fee * FINE_MULTIPLIER
            Payment = apps.get_model('payment', 'Payment')
            Payment.objects.create(
                borrowing=self,
                money_to_pay=fine_amount,
                payment_type='FINE',
                status='PENDING',
            )
            return f"You have a fine of {fine_amount} for returning the book late."
        return "Book returned successfully."
