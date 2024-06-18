from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
)

from payment.serializers import PaymentListSerializer, PaymentDetailSerializer


class PaymentSchema:
    list_schema = (
        extend_schema(
            parameters=[
                OpenApiParameter(
                    name="requested_user",
                    description="Filter by requested user if user is not staff"
                    "Return all if user is staff",
                    required=False,
                    type={"type": "string"},
                ),
            ],
            responses={
                200: PaymentListSerializer(many=True),
            },
        ),
    )

    retrieve = (
        extend_schema(
            responses={
                200: PaymentDetailSerializer(),
            }
        ),
    )

    payment_process_schema = (
        extend_schema(
            request={"application/json": {"borrowing_id": "integer"}},
            responses={
                303: OpenApiParameter(
                    name="redirect_url",
                    description="Redirection to the Stripe payment URL",
                    type={
                        "type": "object",
                        "properties": {"url": {"type": "string"}},
                    },
                    required=["url"],
                ),
                400: OpenApiParameter(
                    name="error",
                    description="Error message",
                    type={
                        "type": "object",
                        "properties": {"error": {"type": "string"}},
                    },
                    required=["error"],
                ),
            },
            description="Create a Stripe payment"
                        " session for a given borrowing ID "
            "and return the URL for the payment.",
        ),
    )

    payment_completed_schema = (
        extend_schema(
            parameters=[
                OpenApiParameter(
                    name="session_id",
                    description="Stripe session ID",
                    required=True,
                    type={"type": "string"},
                )
            ],
            responses={
                200: OpenApiParameter(
                    name="message",
                    description="Payment successful message",
                    type={
                        "type": "object",
                        "properties": {"message": {"type": "string"}},
                    },
                    required=["message"],
                ),
                400: OpenApiParameter(
                    name="error",
                    description="Error message",
                    type={
                        "type": "object",
                        "properties": {"error": {"type": "string"}},
                    },
                    required=["error"],
                ),
            },
            description="Handle the completion of a payment session. "
            "Update the payment status to 'PAID' "
            "if the session ID is valid.",
        ),
    )

    payment_canceled_schema = extend_schema(
        responses={
            200: OpenApiParameter(
                name="message",
                description="Payment canceled message",
                type={
                    "type": "object",
                    "properties": {"message": {"type": "string"}},
                },
                required=["message"],
            ),
        },
        description="Handle the cancellation of a payment session.",
    )
