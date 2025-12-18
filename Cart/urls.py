from django.urls import path
from . import views

urlpatterns = [
    path("add-items/", views.AddItemAPI.as_view(), name="add-items"),
    path("product_in_cart", views.GetProductInCartAPI.as_view(), name='product_in_cart'),
    path("cart", views.GetCart.as_view(), name="cart"),
    path("delete_cartitem/", views.DeleteCartItemAPI.as_view(), name="delete_cartitem"),
    path("update_cartitem/", views.UpdateCartItemAPI.as_view(), name="update_cartitem"),
]





