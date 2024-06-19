from rest_framework import serializers
from borrowing.models import Borrowing
from borrowing.signals import send_pending_payment_notification
from library.models import Book
from payment.models import Payment
from payment.serializers import PaymentSerializer, SelectedPaymentSerializer


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
    book = serializers.CharField(source="book.title")
    author = serializers.CharField(source="book.author")
    cover = serializers.CharField(source="book.cover")
    daily_fee = serializers.IntegerField(source="book.daily_fee")
    payments = SelectedPaymentSerializer(many=True, read_only=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "book",
            "author",
            "cover",
            "borrow_date",
            "daily_fee",
            "expected_return_date",
            "actual_return_date",
            "payments",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True)
    book = serializers.SlugRelatedField(
        slug_field="title", queryset=Book.objects.all()
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )
        read_only_fields = ("borrow_date", "user")

    def validate(self, attrs):
        user = self.context["request"].user
        book = attrs["book"]
        if book.inventory <= 0:
            raise serializers.ValidationError(
                "This book is currently not available for borrowing."
            )
        pending_payments = Payment.objects.filter(
            borrowing__user=user, status="PENDING"
        )
        if pending_payments.exists():
            send_pending_payment_notification(user)
            raise serializers.ValidationError(
                "You have pending payments. "
                "Please complete the payments before borrowing a new book."
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        borrowing = Borrowing.objects.create(user=user, **validated_data)
        return borrowing


class BorrowingReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = ("id", "actual_return_date")

    def update(self, instance, validated_data):
        instance.actual_return_date = validated_data.get(
            "actual_return_date", instance.actual_return_date
        )
        instance.return_borrowing()
        instance.save()
        return instance
