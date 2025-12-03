from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializer import *

# Create your views here.
#GET ALL PRODUCTS
class ProductView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GetAllProductSerializer
    def get(self, request, *args, **kwargs):
        try:
            products = Product.objects.all()
            if products:  
                serializer = self.serializer_class(products, many=True)
                return Response({"products":serializer.data}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        


