from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payment.views import PaymentViewSet, PaymentCompletedView, PaymentCanceledView, PaymentProcessView

router = DefaultRouter()
router.register("payment", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
    path("process/", PaymentProcessView.as_view(), name="process"),
    path("completed/", PaymentCompletedView.as_view(), name="completed"),
    path("canceled/", PaymentCanceledView.as_view(), name="canceled"),
]

app_name = "payment"
