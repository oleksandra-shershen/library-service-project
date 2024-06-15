from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.apps import apps


from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from rest_framework.permissions import IsAuthenticated


class BorrowingViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all().select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

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

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_staff:
            user_id = self.request.query_params.get("user_id")
            if user_id:
                queryset = queryset.filter(user_id=user_id)
        else:
            queryset = queryset.filter(user=self.request.user)

        is_active = self.request.query_params.get("is_active")
        if is_active:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.exclude(actual_return_date__isnull=True)

        return queryset

    @action(detail=True, methods=["POST"], url_path="return")
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()
        serializer = self.get_serializer(
            borrowing, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def process_return_borrowing(self, borrowing):
        borrowing.actual_return_date = timezone.now().date()
        borrowing.save()

        if borrowing.actual_return_date > borrowing.expected_return_date:
            overdue_days = (borrowing.actual_return_date - borrowing.expected_return_date).days
            fine_amount = overdue_days * borrowing.book.daily_fee * 2
            Payment = apps.get_model('payment', 'Payment')
            Payment.objects.create(
                borrowing=borrowing,
                money_to_pay=fine_amount,
                payment_type='FINE',
                status='PENDING',
            )
            return {"message": f"You have a fine of {fine_amount} for returning the book late."}
        else:
            return {"message": "Book returned successfully."}
