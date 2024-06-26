from django.urls import path, include
from rest_framework.routers import DefaultRouter
from library.views import BookViewSet


router = DefaultRouter()
router.register("books", BookViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "library"
