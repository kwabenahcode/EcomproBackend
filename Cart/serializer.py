from rest_framework import serializers
from .models import *
from Product.serializer import *

from decimal import Decimal


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total = serializers.SerializerMethodField()
    class Meta:
        model = CartItem
        fields = ["id", "product", "quantity", "total"]

    def get_total(self, cartitem):
        price = cartitem.product.price * cartitem.quantity
        return price

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(read_only=True, many=True)
    number_of_items = serializers.SerializerMethodField()
    sum_total = serializers.SerializerMethodField()
    class Meta:
        model = Cart
        fields = ["id","cart_code", "items", "sum_total","number_of_items", "created_at", "modified_at"]

    def get_number_of_items(self, cart):
        items = cart.items.all()
        number_of_items = sum([item.quantity for item in items])
        return number_of_items
    
    def get_sum_total(self, cart):
        items = cart.items.all()
        total = sum([item.product.price * item.quantity  for item in items])
        return total
    
    
        

