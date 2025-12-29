from rest_framework import serializers
from Product.serializer import *
from .models import *

class OrderItemSerializer(serializers.ModelSerializer):
    product = GetAllProductSerializer()

    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price"]


class OrderSerializer(serializers.ModelSerializer):
    orderitems = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            "order_id",
            "status",
            "total_amount",
            "created_at",
            "orderitems",
        ]
