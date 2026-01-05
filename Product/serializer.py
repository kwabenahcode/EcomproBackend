from rest_framework import serializers
from .models import *

class GetAllProductSerializer(serializers.ModelSerializer):
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["id","name","category", "image", "price", "description", "slug", "average_rating", "total_ratings"]

    def get_average_rating(self, product):
        return (product.average_rating)  # optional rounding

    def get_total_ratings(self, product):
        return product.total_ratings 
    
    
class GetSingleProductSerializer(serializers.ModelSerializer):
    related_product = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["id","name","category", "image", "price", "description", "slug", "related_product", "average_rating", "total_ratings"] 

    def get_related_product(self, product):
        products = Product.objects.filter(category=product.category).exclude(id=product.id)
        serializer=GetAllProductSerializer(products, many=True)
        return serializer.data
    
    def get_average_rating(self, product):
        return round(product.average_rating, 2)  # optional rounding

    def get_total_ratings(self, product):
        return product.total_ratings
    
    

class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["score"]

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Score must be between 1 and 5")
        return value