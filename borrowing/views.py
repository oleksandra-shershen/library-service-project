from rest_framework import viewsets
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingListSerializer,
    BorrowingDetailSerializer,
)
from rest_framework.permissions import IsAuthenticated


class BorrowViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.all().select_related("book", "user")
    serializer_class = BorrowingSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        elif self.action == "retrieve":
            return BorrowingDetailSerializer
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
