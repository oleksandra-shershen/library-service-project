from rest_framework import mixins, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.urls import reverse

from library_service import settings
from .models import Payment
from .serializers import PaymentSerializer, PaymentListSerializer, PaymentDetailSerializer
import stripe

stripe.api_key = settings.STRIPE_PUBLISHABLE_KEY


def create_payment_session(borrowing, request):
    amount = int(float(borrowing.get_total_price('PAYMENT')) * 100)  # Convert to cents
    success_url = request.build_absolute_uri(reverse('payment_success'))
    cancel_url = request.build_absolute_uri(reverse('payment_cancel'))

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': borrowing.book.title,
                },
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=success_url,
        cancel_url=cancel_url,
    )

    payment = Payment.objects.create(
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=amount / 100,  # Convert back to dollars
        payment_type='PAYMENT',
    )
    return payment


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


@api_view(['GET'])
def payment_success(request):
    session_id = request.GET.get('session_id')
    session = stripe.checkout.Session.retrieve(session_id)

    if session.payment_status == 'paid':
        payment = get_object_or_404(Payment, session_id=session_id)
        payment.status = 'PAID'
        payment.save()
        return Response({'status': 'Payment successful'})
    return Response({'status': 'Payment not successful'}, status=400)


@api_view(['GET'])
def payment_cancel(request):
    return Response({'status': 'Payment can be completed within 24 hours'})
