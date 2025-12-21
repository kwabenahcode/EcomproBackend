from rest_framework import serializers
from .models import *

class RegisterUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=4)
    class Meta:
        model = User
        fields = ["full_name", "email", "password"]

    def create(self, validated_data):
        #Clean the data coming from the frontend
        email = validated_data["email"].lower()
        full_name = validated_data["full_name"]
        
        user = User.objects.create(
            email=email,
            full_name=full_name
            )
        user.set_password(validated_data["password"])
        user.save()
        return user




        
