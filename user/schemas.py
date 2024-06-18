from drf_spectacular.utils import (
    extend_schema,
)


class UserSchema:
    create = extend_schema(
        responses={201: "User created successfully", 400: "Bad request"},
        description="Create a new user.",
    )

    manage_user_schema = extend_schema(
        responses={
            200: "User details retrieved/updated successfully",
            401: "Unauthorized",
            400: "Bad request",
        },
        description="Retrieve or update the authenticated user's details.",
    )

    save_chat_id_schema = extend_schema(
        request={"application/json": {"email": "string", "chat_id": "string"}},
        responses={
            200: "Chat ID saved successfully",
            404: "User not found",
            400: "Bad request",
        },
        description="Save the Telegram chat"
                    " ID for a user identified by email.",
    )
