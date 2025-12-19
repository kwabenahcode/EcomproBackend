from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response

from .serializer import *

# Create your views here.
#GET ALL PRODUCTS
class ProductView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = GetAllProductSerializer
    queryset = Product.objects.all()

    def get(self, request, *args, **kwargs):
        slug = kwargs.get("slug") 
        if slug:
            return self.get_single_product(slug)
        else:
            return self.get_all_products()
        
        
    def get_single_product(self, slug):
        try:
            product = self.get_queryset().get(slug=slug)
            serializer = GetSingleProductSerializer(product)
            return Response({"status":"success","product":serializer.data}, status=200)
        except Exception as e:
            return Response({"error":"No product found"}, status=404)

    def get_all_products(self):
        try:
            products = self.get_queryset()
            serializer = self.serializer_class(products, many=True)
            return Response({"products": serializer.data}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
        

class GetProductCategory(generics.GenericAPIView):
    permission_classes=[permissions.AllowAny]
    serializer_class = GetAllProductSerializer
    # queryset = Product

    def get(self, request, *args, **kwargs):
        category = kwargs.get("category")
        products_category = Product.objects.filter(category__iexact=category)
        serializer = self.serializer_class(products_category, many=True)
        return Response({"category":serializer.data}, status=200)
    

class RateProductView(generics.GenericAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.AllowAny]  # User must be logged in

    def post(self, request, *args, **kwargs):
        slug = kwargs.get("slug")

        # 1. Get product by slug
        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        score = request.data.get("score")  # value from frontend

         # 2. Validate score (must be 1–5)
        try:
            score = int(score)
        except:
            return Response({"error": "Invalid score"}, status=400)

        if score < 1 or score > 5:
            return Response({"error": "Score must be between 1 and 5"}, status=400)

        user = request.user

        # 3. Create or update rating
        rating_obj, created = Rating.objects.get_or_create(
            product=product,
            user=user,
            defaults={"score": score}
        )

        if not created:
            rating_obj.score = score
            rating_obj.save()

        # 4. Recalculate product rating
        all_ratings = Rating.objects.filter(product=product)
        product.total_ratings = all_ratings.count()
        product.sum_ratings = sum(r.score for r in all_ratings)
        product.save()

        return Response(
            {"message": "Rating saved successfully"},
            status=200
        )
    


        


