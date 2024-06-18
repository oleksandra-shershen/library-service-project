from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from django.utils import timezone
from django.apps import apps

from borrowing.models import Borrowing
from borrowing.schemas import BorrowingSchema
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from rest_framework.permissions import IsAuthenticated


@method_decorator(name="list", decorator=BorrowingSchema.list_schema)
@method_decorator(name="retrieve", decorator=BorrowingSchema.retrieve)
@method_decorator(
    name="return_borrowing", decorator=BorrowingSchema.return_borrowing
)
class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Borrowing.objects.all().select_related("book", "user")
        is_active = self.request.query_params.get("is_active")
        user = self.request.user

        if user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=self.request.user)

        if is_active:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.exclude(actual_return_date__isnull=True)

        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
        elif self.action == "create":
            return BorrowingCreateSerializer
        elif self.action == "return_borrowing":
            return BorrowingReturnSerializer
        return self.serializer_class

    @action(detail=True, methods=["POST"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(
            borrowing, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()

            borrowing.actual_return_date = timezone.now().date()
            borrowing.save()

            if borrowing.actual_return_date > borrowing.expected_return_date:
                overdue_days = (
                    borrowing.actual_return_date
                    - borrowing.expected_return_date
                ).days
                fine_amount = overdue_days * borrowing.book.daily_fee * 2
                payment = apps.get_model("payment", "Payment")
                payment.objects.create(
                    borrowing=borrowing,
                    money_to_pay=fine_amount,
                    payment_type="FINE",
                    status="PENDING",
                )
                return Response(
                    {
                        "message": f"You have"
                        f" a fine of {fine_amount}"
                        f" for returning the book late."
                    }
                )
            else:
                return Response({"message": "Book returned successfully."})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        borrowing = serializer.save()
        try:
            borrowing.create_stripe_session()
        except Exception as e:
            borrowing.delete()
            raise ValidationError(f"Error creating Stripe session: {e}")

    @method_decorator(cache_page(60 * 60))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
