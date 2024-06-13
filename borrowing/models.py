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
            f"{self.book}: from {self.borrow_date} "
            f"to {self.expected_return_date}."
        )

    def clean(self):
        if self.actual_return_date and self.actual_return_date < self.borrow_date:
            raise ValidationError("Actual return date cannot be before the borrow date.")
        if self.expected_return_date < self.borrow_date:
            raise ValidationError("Expected return date cannot be before the borrow date.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

