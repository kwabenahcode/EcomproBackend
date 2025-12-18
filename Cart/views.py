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
        
            cartitem.quantity =1
            cartitem.save()

            serializer = self.serializer_class(cartitem)
            return Response({"data": serializer.data, "message":"Cart Item Added Successfully"}, status=200, )
        except Exception as e:
            return Response({"The error":str(e)}, status=400)
        

class GetProductInCartAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CartItemSerializer

    def get(self, request):
        cart_code = request.query_params.get('cart_code')
        product_id = request.query_params.get('product_id')

        cart = Cart.objects.get(cart_code=cart_code)
        product = Product.objects.get(id=product_id)

        product_exist_in_cart = CartItem.objects.filter(cart=cart, product=product).exists()
        print("This product is: " , product_exist_in_cart)
        return Response({"Product_in_Cart":product_exist_in_cart})
    
class GetCart(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CartSerializer

    def get(self, request):
        try:
            cart_code = request.query_params.get("cart_code")
            cart = Cart.objects.get(cart_code=cart_code,  paid=False)
            serializer = CartSerializer(cart)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)})

class DeleteCartItemAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CartItemSerializer

    def post(self, request):
        cartitem_id = request.data.get("item_id")
        cartitem = CartItem.objects.get(id=cartitem_id)  
        cartitem.delete()
        return Response({"message":"CartItem Deleted Successfully"}, status=200)


class UpdateCartItemAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = CartItemSerializer()

    def patch(self, request):
        try:
            cartitem_id = request.data.get("item_id")
            quantity = request.data.get("quantity")
            quantity = int(quantity)
            cartitem = CartItem.objects.get(id=cartitem_id)
            cartitem.quantity = quantity
            cartitem.save()
            serializer = CartItemSerializer(cartitem)
            return Response({"data": serializer.data, "message": "Cart Item updated successfully"}, status=200)
        except Exception as e:
            return Response({"error": str(e)})   
        


