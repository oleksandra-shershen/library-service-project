from rest_framework import viewsets, mixins

from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentListSerializer


class PaymentViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.select_related("borrowing__book", "borrowing__user")

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return PaymentListSerializer
        return PaymentSerializer
