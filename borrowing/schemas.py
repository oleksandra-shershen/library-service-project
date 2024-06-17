from drf_spectacular.utils import extend_schema, OpenApiParameter

from borrowing.serializers import (
    BorrowingListSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer
)


class BorrowingSchema:
    list = extend_schema(
        parameters=[
            OpenApiParameter(
                name="is_active",
                description="Filter by active status (true/false)",
                required=False,
                type={"type": "string"},
            ),
            OpenApiParameter(
                name="user_id",
                description="Filter by user ID (staff only)",
                required=False,
                type={"type": "string"},
            ),
        ],
        responses={
            200: BorrowingListSerializer(many=True),
        },
    )
    retrieve = extend_schema(
        responses={
            200: BorrowingDetailSerializer()
        },
    )
    return_borrowing = extend_schema(
        responses={
            200: BorrowingReturnSerializer()
        }
    )
