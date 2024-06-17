from drf_spectacular.utils import (
    extend_schema,
)

from library.serializers import BookSerializer


class BookSchema:
    list_schema = extend_schema(
        responses={
            200: BookSerializer(many=True),
        }
    )
    retrieve = extend_schema(
        responses={
            200: BookSerializer(many=True),
        }
    )
