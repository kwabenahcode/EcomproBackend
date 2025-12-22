from django.urls import path
from . import views

urlpatterns = [
    path("auth/register_user/", views.RegisterUserAPI.as_view(), name="register_user"),
    path("auth/login/", views.UserLoginAPI.as_view(), name="login"),
    path("/get_email", views.GetEmailAPI.as_view(), name="get_email")
]