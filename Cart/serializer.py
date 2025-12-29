from rest_framework import serializers
from .models import *
from Product.serializer import *

from decimal import Decimal


class CartItemSerializer(serializers.ModelSerializer):
    product = GetAllProductSerializer(read_only=True)
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
    
class NewCartItemSerializer(serializers.ModelSerializer):
    product = GetAllProductSerializer(read_only=True)
    order_id = serializers.SerializerMethodField()
    order_date = serializers.SerializerMethodField()
    paid = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = ["product", "order_id", "order_date", "quantity", "paid"]

    def get_order_id(self, cartitem):
        order_id = cartitem.cart.cart_code
        return order_id
    
    def get_order_date(self, cartitem):
        order_date = cartitem.cart.modified_at
        return order_date
    
    def get_paid(self, cartitem):
        paid = cartitem.cart.paid
        return paid


    
    
        

