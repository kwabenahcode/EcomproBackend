from django.urls import path
from . import views

urlpatterns = [
    path("add-items/", views.AddItemAPI.as_view(), name="add-items"),
    
]