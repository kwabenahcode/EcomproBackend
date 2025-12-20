from rest_framework import serializers
from .models import *

class GetAllProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id","name","category", "image", "price", "description", "slug"] 
    
    
class GetSingleProductSerializer(serializers.ModelSerializer):
    related_product = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["id","name","category", "image", "price", "description", "slug", "related_product"] 

    def get_related_product(self, product):
        products = Product.objects.filter(category=product.category).exclude(id=product.id)
        serializer=GetAllProductSerializer(products, many=True)
        return serializer.data
    
    

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["product", "user", "score"]

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Score must be between 1 and 5")
        return value