from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/borrowing/", include("borrowing.urls", namespace="borrowing")),
    path("api/library/", include("library.urls", namespace="library")),
    path("api/payment/", include("payment.urls", namespace="payment")),
    path("api/user/", include("user.urls", namespace="user")),
]
