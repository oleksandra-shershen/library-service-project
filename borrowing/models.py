from datetime import timezone

from django.db import models
from rest_framework.exceptions import ValidationError

from library.models import Book
from library_service import settings


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
        if self.actual_return_date is not None:
            raise ValidationError("This borrowing has already been returned.")
        self.actual_return_date = timezone.now().date()
        self.book.inventory += 1
        self.book.save()
        self.save()

    def get_total_price(self, payment_type: str) -> str:
        book_price = self.book.daily_fee
        if payment_type == "PAYMENT":
            count_of_days = self.expected_return_date - self.borrow_date
        if payment_type == "FINE":
            count_of_days = self.actual_return_date - self.expected_return_date
        return str(round(book_price * count_of_days.days, 2))
