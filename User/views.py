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

            user = serializer.save()
            user.save()
            return Response({"status": "success", "message": "User registered successfully", "user_data":serializer.data},
                status=status.HTTP_201_CREATED,
            )
        else:
            print(serializer.errors)
            
            # Extract the first error message in a simpler format
            errors = {}
            for field, error_list in serializer.errors.items():
                # Extract the actual error message string
                if isinstance(error_list, list) and len(error_list) > 0:
                    if hasattr(error_list[0], 'string'):
                        errors[field] = error_list[0].string
                    else:
                        errors[field] = str(error_list[0])
                else:
                    errors[field] = str(error_list)
            
            # Get the first error for the general message
            first_error = next(iter(errors.values())) if errors else "Registration failed"
            
            return Response({
                "status": "failure",
                "message": first_error,
                "errors": errors  # Include all errors if needed
            }, status=status.HTTP_400_BAD_REQUEST)