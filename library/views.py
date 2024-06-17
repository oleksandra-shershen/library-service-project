from django.utils.decorators import method_decorator
from rest_framework import viewsets
from library.models import Book
from library.permissions import IsAdminOrIfAuthenticatedReadOnly
from library.schemas import BookSchema
from library.serializers import BookSerializer


@method_decorator(name="list", decorator=BookSchema.list)
@method_decorator(name="retrieve", decorator=BookSchema.retrieve)
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAdminOrIfAuthenticatedReadOnly]
