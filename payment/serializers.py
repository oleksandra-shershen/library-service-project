from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "borrowing",
            "status",
            "type",
            "session_url",
            "session_id",
            "money_to_pay",
            "created_at",
            "updated_at",
        )


class PaymentListSerializer(serializers.ModelSerializer):
    borrowing = serializers.CharField(source="borrowing.id", read_only=True)
    book = serializers.CharField(source="borrowing.book.title", read_only=True)
    user = serializers.CharField(source="borrowing.user.email", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "borrowing",
            "book",
            "user",
            "status",
            "type",
            "money_to_pay",
        )


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing = serializers.CharField(source="borrowing.id", read_only=True)
    book = serializers.CharField(source="borrowing.book.title", read_only=True)
    user = serializers.CharField(source="borrowing.user.email", read_only=True)

    class Meta:
        model = Payment
        fields = (
            "id",
            "borrowing",
            "book",
            "user",
            "status",
            "type",
            "session_url",
            "session_id",
            "money_to_pay",
            "created_at",
            "updated_at",
        )
