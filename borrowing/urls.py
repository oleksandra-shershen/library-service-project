from django.urls import path, include
from rest_framework.routers import DefaultRouter
from borrowing.views import BorrowViewSet

router = DefaultRouter()
router.register("borrowings", BorrowViewSet, basename="borrowing")

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "borrowing"
