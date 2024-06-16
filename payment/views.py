import stripe
from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.reverse import reverse

from payment.models import Payment
from payment.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
)
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY
stripe.api_version = settings.STRIPE_API_VERSION


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = PaymentSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            queryset = Payment.objects.all().select_related(
                "borrowing__book", "borrowing__user"
            )
        else:
            queryset = Payment.objects.filter(borrowing__user=user).select_related(
                "borrowing__book", "borrowing__user"
            )

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        elif self.action == "retrieve":
            return PaymentDetailSerializer
        return self.serializer_class


class PaymentProcessView(APIView):
    def post(self, request, *args, **kwargs):
        borrowing_id = request.data.get("borrowing_id")
        borrowing = get_object_or_404(Payment, borrowing_id=borrowing_id)

        success_url = request.build_absolute_uri(reverse("payment:completed"))
        cancel_url = request.build_absolute_uri(reverse("payment:canceled"))

        session_data = {
            "mode": "payment",
            "client_reference_id": borrowing.id,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "line_items": []
        }

        session_data["line_items"].append({
            "price_data": {
                "unit_amount": int(
                    borrowing.borrowing.calculate_total_price()
                    * Decimal("100")
                ),
                "currency": "usd",
                "product_data": {
                    "name": borrowing.borrowing.book.title,
                },
            },
            "quantity": 1,
        })

        try:
            session = stripe.checkout.Session.create(**session_data)
            return Response(
                {"url": session.url},
                status=status.HTTP_303_SEE_OTHER
            )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentCompletedView(APIView):
    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response(
                {"error": "Session ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = Payment.objects.get(session_id=session_id)
            payment.status = "PAID"
            payment.save()
            return Response(
                {"message": "Payment successful"},
                status=status.HTTP_200_OK
            )
        except Payment.DoesNotExist:
            return Response(
                {"error": "Invalid session ID"},
                status=status.HTTP_400_BAD_REQUEST
            )


class PaymentCanceledView(APIView):
    def get(self, request, *args, **kwargs):
        return Response(
            {"message": "Payment canceled"},
            status=status.HTTP_200_OK
        )
