from django.urls import path, include
from rest_framework.routers import DefaultRouter
from payment.views import PaymentViewSet, payment_success, payment_cancel

router = DefaultRouter()
router.register("payment", PaymentViewSet, basename="payment")

urlpatterns = [
    path("", include(router.urls)),
    path('success/', payment_success, name='payment_success'),
    path('cancel/', payment_cancel, name='payment_cancel'),
]

app_name = "payment"
