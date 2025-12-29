from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path("auth/register_user/", views.RegisterUserAPI.as_view(), name="register_user"),
    path("auth/login/", views.UserLoginAPI.as_view(), name="login"),
    path("get_email", views.GetEmailAPI.as_view(), name="get_email"),
    path("user_profile", views.GetUserProfileAPI.as_view(),name="user_profile"),
]