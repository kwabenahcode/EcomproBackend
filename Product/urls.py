from django.urls import path
from . import views

urlpatterns = [
    path("products", views.ProductView.as_view(), name="products"),
    path("product-details/<slug:slug>", views.ProductView.as_view(), name="product-details"),
]