from django.db import models

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
                check=models.Q(expected_return_date__gte=models.F("borrow_date")),
                name="expected_return_date_gte_borrow_date"
            ),
            models.CheckConstraint(
                check=models.Q(actual_return_date__gte=models.F("borrow_date")),
                name="actual_return_date_gte_borrow_date"
            ),
        ]
