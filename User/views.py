from django.shortcuts import render
from rest_framework import generics, permissions,status
from rest_framework.response import Response
from .serializers import *

import re

# Create your views here.
class RegisterUserAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterUserSerializer

    def post(self, request, *agrs, **kwargs):
        serializer = self.serializer_class(data=request.data)
        #condition to check if serializer is valid(meaning if everything the backend is expecting from the frontend is intact)
        if serializer.is_valid():
            email = serializer.data["email"]
            full_name = serializer.data["full_name"]
            password = serializer.data["password"]

             # Validate password
            if len(password) < 4:
                return Response({"status":"Failure", "message":"Password must be more than 4"}, status=400)
            
            #validate email format
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return Response(
                    {"status": "failure", "message": "Invalid email address format"},
                    status=400,
                )
            
            #check if email already exist
            if User.objects.filter(email=email):
                return Response({"status":"failure", "message":"Email already exist"}, 
                                status=400
                                )
            
            user = User.objects.create(email=email, full_name=full_name)
            user.set_password(password)
            user.save()
            return Response({"status": "success", "message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"status": "failure", "detail": serializers.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
