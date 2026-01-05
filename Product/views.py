from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

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
            product_data = serializer.data

            if self.request.user.is_authenticated:
                user_rating = Rating.objects.filter(product=product, user=self.request.user).first()
                product_data['user_rating'] = user_rating.score if user_rating else None
            return Response({"status": "success", "product": product_data}, status=200)
            
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
    

class RateProductView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        product = get_object_or_404(Product, slug=kwargs['slug'])
        user = request.user

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        score = serializer.validated_data['score']

        rating, created = Rating.objects.get_or_create(
            product=product,
            user=user,
            defaults={'score': score}
        )

        if not created:
            # Update rating
            product.sum_ratings -= rating.score
            rating.score = score
            rating.save()
            product.sum_ratings += score
        else:
            product.sum_ratings += score
            product.total_ratings += 1

        product.save()

        return Response({
            "average_rating": product.average_rating,
            "total_ratings": product.total_ratings
        }, status=200)

    


        


