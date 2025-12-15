from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializer import *

# Create your views here.
class AddItemAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CartItemSerializer

    def post(self, request):
        try:
            cart_code = request.data.get("cart_code")
            product_id = request.data.get("product_id")

            cart, created = Cart.objects.get_or_create(cart_code=cart_code)
            product = Product.objects.get(id=product_id)

            cartitem, created = CartItem.objects.get_or_create(cart=cart, product=product)
            cartitem.quantity +=1
            cartitem.save()

            serializer = self.serializer_class(cartitem)
            return Response({"data": serializer.data, "message":"Cart Item Added Successfully"}, status=200, )
        except Exception as e:
            return Response({"The error":str(e)}, status=400)
        


