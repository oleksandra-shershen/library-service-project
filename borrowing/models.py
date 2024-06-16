from datetime import timezone, datetime
import stripe

from django.db import models
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
