from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from borrowing.models import Borrowing
from library.serializers import BookSerializer
from payment.serializers import PaymentSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )
        read_only_fields = ("borrow_date", "user")

    def validate(self, attrs):
        book = attrs.get("book")
        if book.inventory < 1:
            raise ValidationError("This book is not available for borrowing.")
        return attrs

    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        validated_data["user"] = self.context["request"].user
        borrowing = super().create(validated_data)
        return borrowing


class BorrowingListSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.email", read_only=True)
    book = serializers.CharField(source="book.title", read_only=True)
    author = serializers.CharField(source="book.author", read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "author",
            "user",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "payments",
        )
