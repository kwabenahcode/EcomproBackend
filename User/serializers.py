from rest_framework import serializers
from .models import *
from Cart.serializer import *
from Orders.models import *
from Orders.serializers import *

class RegisterUserSerializer(serializers.ModelSerializer):
    # password = serializers.CharField(write_only=True, min_length=4)
    class Meta:
        model = User
        fields = ["full_name", "email", "password"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        #Clean the data coming from the frontend
        email = validated_data["email"].lower()
        full_name = validated_data["full_name"]
        password = validated_data["password"]

        user = User.objects.create(
            email=email,
            full_name=full_name
            )
        user.set_password(password)
        user.save()
        return user
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    

# class UserSerializer(serializers.ModelSerializer):
#     items = serializers.SerializerMethodField()
#     class Meta:
#         model = User
#         fields = ["email", "full_name", "state", "image", "address","items" ]

#     def get_items(self, user):
#         cartitems = CartItem.objects.filter(cart__user=user, cart__paid=True)[:10]
#         serializer = NewCartItemSerializer(cartitems, many=True)
#         return serializer.data

class UserSerializer(serializers.ModelSerializer):
    orders = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["email", "full_name", "state", "image", "address", "orders"]

    def get_orders(self, user):
        orders = Order.objects.filter(user=user).order_by("-created_at")
        return OrderSerializer(orders, many=True).data
    
class UpdateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "full_name",
            "state",
            "address",
            "image",
            "email"
        ]







        
