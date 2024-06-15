from rest_framework import serializers
from borrowing.models import Borrowing
from library.serializers import BookSerializer
from payment.serializers import PaymentSerializer
from payment.views import create_payment_session


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


class BorrowingCreateSerializer(serializers.ModelSerializer):
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
        book = attrs["book"]
        if book.inventory <= 0:
            raise serializers.ValidationError(
                "This book is currently not available for borrowing."
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(user=user, **validated_data)

        request = self.context.get("request")
        create_payment_session(borrowing, request)
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")

    def update(self, instance, validated_data):
        instance.return_borrowing()
        return instance
