from rest_framework import serializers
from .models import *
from Product.serializer import *

from decimal import Decimal


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity"]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(read_only=True, many=True)
    number_of_items = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ["id","cart_code", "items", "total","number_of_items", "created_at", "modified_at"]

    def get_number_of_items(self, cart):
        items = cart.items.all()
        number_of_items = sum([item.quantity for item in items])
        return number_of_items
    
    def get_total(self, cart):
        items = cart.items.all()
        total = sum([item.product.price * item.quantity  for item in items])
        return total
    
    
        

