from django.urls import path
from . import views

urlpatterns = [
    path("initiate_payment/", views.InitiatePaymentAPI.as_view(), name="initiate_payment"),
    path("payment_callback/", views.PaymentCallBackAPI.as_view(), name="payment_callback"),
]