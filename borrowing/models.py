from datetime import timezone, datetime
import stripe
from datetime import date
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.conf import settings
from library.models import Book


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

    def clean(self):
        if not self.borrow_date:
            self.borrow_date = date.today()

        if (self.expected_return_date
                and self.expected_return_date < self.borrow_date):
            raise ValidationError(
                "Expected return date cannot be before the borrow date."
            )

        if (self.actual_return_date
                and self.actual_return_date < self.borrow_date):
            raise ValidationError(
                "Actual return date cannot be before the borrow date."
            )

        if not self.pk and self.book.inventory < 1:
            raise ValidationError(
                f"The book '{self.book.title}' is not available for borrowing."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def return_borrowing(self):
        if self.actual_return_date is not None:
            raise ValidationError("This borrowing has already been returned.")
        self.actual_return_date = timezone.now().date()
        self.book.inventory += 1
        self.book.save()
        self.save()

    def calculate_total_price(self):
        today = datetime.now().date()
        days_borrowed = (self.expected_return_date - today).days
        total_price = self.book.daily_fee * days_borrowed
        total_price = int(total_price * 100)    # Stripe expects amount in cents
        return total_price

    def create_stripe_session(self):
        from payment.models import Payment  # Lazy import
        stripe.api_key = settings.STRIPE_SECRET_KEY

        total_price = self.calculate_total_price()

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": self.book.title,
                    },
                    "unit_amount": total_price,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://localhost:8000/api/payment/completed/" + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://localhost:8000/api/payment/canceled/"
        )

        payment = Payment.objects.create(
            borrowing=self,
            session_url=session.url,
            session_id=session.id,
            money_to_pay=total_price,
            status="PENDING",
        )

        return payment
