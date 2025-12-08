from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["category"] 

class GetAllProductSerializer(serializers.ModelSerializer):
    product_category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_product_category(self, product):
        result = Product.objects.filter(category=product.category)
        serializer=ProductSerializer(result, many=True)
        return serializer.data
