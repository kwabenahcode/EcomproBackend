from rest_framework import serializers
from .models import *

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id","name","category", "image", "price", "description", "slug"] 

class GetAllProductSerializer(serializers.ModelSerializer):
    product_category = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_ratings = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = "__all__"

    def get_product_category(self, product):
        result = Product.objects.filter(category=product.category)
        serializer=ProductSerializer(result, many=True)
        return serializer.data
    
    def get_average_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings.exists():
            return round(sum(r.score for r in ratings) / ratings.count(), 1)
        return 0

    def get_total_ratings(self, obj):
        return obj.ratings.count()
    
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ["product", "user", "score"]

    def validate_score(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Score must be between 1 and 5")
        return value


