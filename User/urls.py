from django.urls import path
from . import views

urlpatterns = [
    path("auth/register_user/", views.RegisterUserAPI.as_view(), name="register_user"),
]