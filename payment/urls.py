from django.urls import path
from . import views

# urlpatterns = [
#     path("initiate_payment/", views.InitiatePaymentAPI.as_view(), name="initiate_payment"),
#     path("payment_callback/", views.PaymentCallBackAPI.as_view(), name="payment_callback"),
#     path("payment-status/", views.PaymentCallBackAPI.as_view(), name="payment_status"),
# ]

urlpatterns = [
    path("initiate_payment/", views.InitiatePaymentAPI.as_view(), name="initiate_payment"),

    # Paystack redirects here (AllowAny + redirect to frontend)
    path("payment_callback/", views.PaymentCallBackAPI.as_view(), name="payment_callback"),

    # React calls this (Authenticated + JSON response)
    path("payment-status/", views.PaymentStatusAPI.as_view(), name="payment_status"),
]