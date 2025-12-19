from django.shortcuts import render
from rest_framework import generics, permissions
from .serializers import *

# Create your views here.
class RegisterUserAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterUserSerializer

    