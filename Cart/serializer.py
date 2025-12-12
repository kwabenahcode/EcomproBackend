from rest_framework import serializers
from .models import *

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ["id","user", "cart", "quantity", "paid", "cart_code"]


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ["id", "product", "cart", "quantity"]
        

