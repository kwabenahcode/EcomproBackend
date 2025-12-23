from django.shortcuts import render
from rest_framework import generics, permissions,status
from rest_framework.response import Response
from .serializers import *
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

import re

# Create your views here.
class RegisterUserAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterUserSerializer

    def post(self, request, *agrs, **kwargs):
        serializer = self.serializer_class(data=request.data)

        #condition to check if serializer is valid(meaning if everything the backend is expecting from the frontend is intact)
        if (serializer.is_valid()):
            email = serializer.data["email"]
            full_name = serializer.data["full_name"]
            password = serializer.validated_data["password"]

            if len(password) < 4:
                return Response ({
                    "status":"Failure",
                    "detail":"Email cannot be less than 4 characters"
                },
                status=400
                )
            
            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                return Response(
                    {"status": "failure", 
                     "detail": "Invalid email address format"
                    },
                    status=400,
                )
            
            if User.objects.filter(email=email):
                return Response({
                    "status": "Failure",
                    "detail":"Email already Exist"
                },
                status=400,
                )
            
            user = User.objects.create(
                email=email,
                full_name =full_name,
            )

            user.set_password(password)
            user.save()
            return Response(
                {
                    "status": "success",
                    "detail":"registered Successfully",  
                    "user_data":RegisterUserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            print(serializer.errors)
            return Response(
                {"status": "failure", "detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        

class UserLoginAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]

            if not User.objects.filter(email=email).exists():
                return Response({
                    "status":"failure",
                    "detail":"Invalid credentialss"
                },
                status=400
                )
            user = authenticate(email=email, password=password)
            if not user:
                return Response({
                    "status":"failure",
                    "detail": "User Not Found"
                },
                status=400
                )
            refresh = RefreshToken.for_user(user)
            context = {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
            return Response({
                    "status":"Success",
                    "detail":"User Login Successfully",
                    "refresh":context["refresh"],
                    "access":context["access"],
                    "user": UserLoginSerializer(user).data
                },
                status=200
                )
        else:
            print(serializer.errors)
            return Response ({
                "status":"failure",
                "detail":serializer.errors
            },
            status=400
            )
        
class GetEmailAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            "email":user.email
        })
    
# class RefreshTokenAPI(generics.GenericAPIView):
#     permission_classes = [permissions.AllowAny]

#     def post(self, request):
#         refresh = request.get("access")
#         if not is_valid_refresh(refresh):
#             return Response(status=401)

#         new_access = generate_access_token(user)
#         return Response({"access": new_access})
    