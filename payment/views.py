import stripe
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated

from borrowing.models import Borrowing
from library_service import settings
from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
)

stripe.api_key = settings.STRIPE_PUBLISHABLE_KEY


def create_session(book_title: str, unit_amount: int) -> (str, str):
    if stripe.api_key:
        session = stripe.checkout.Session.create(
            line_items=[{
                "price_data": {
                    "currency": "usd",
                    "product_data": {"name": book_title},
                    "unit_amount": unit_amount,
                },
                "quantity": 1
            }],
            mode="payment",
            success_url="http://127.0.0.1:8001/api/payment/payment/success/",
            cancel_url="http://127.0.0.1:8001/api/payment/payment/cancel/",
        )
        return session.url, session.id
    return "", ""


def create_payment(borrowing: Borrowing, payment_type: str):
    money_to_pay = borrowing.get_total_price(payment_type)
    book_title = borrowing.book.title
    unit_amount = int(money_to_pay.replace(".", ""))
    session_url, session_id = create_session(book_title, unit_amount)

    Payment.objects.create(
        borrowing=borrowing,
        payment_status="PENDING",
        payment_type=payment_type,
        session_url=session_url,
        session_id=session_id,
        money_to_pay=float(money_to_pay),
    )


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.all().select_related(
        "borrowing__book", "borrowing__user"
    )
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all().select_related(
                "borrowing__book", "borrowing__user"
            )
        return Payment.objects.filter(borrowing__user=user).select_related(
            "borrowing__book", "borrowing__user"
        )

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        elif self.action == "retrieve":
            return PaymentDetailSerializer
        return self.serializer_class
