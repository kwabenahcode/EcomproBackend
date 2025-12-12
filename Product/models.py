from django.db import models
import uuid
from User.models import *
from django.utils.text import slugify

# Create your models here.
class Product(models.Model):
    CATEGORY = (
        ('Groceries', 'GROCERIES'),
        ('Fashion', 'FASHION'),
        ('Electronics', 'ELECTRONICS'),
        ('Furniture', 'FURNITURE'),
        ('Beauty', "BEAUTY")
    )
    slug = models.SlugField(blank=True,null=True, unique=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(max_length=500,  blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    image = models.ImageField(upload_to="product_images", blank=True, null=True)
    category = models.CharField(choices=CATEGORY, max_length=15, blank=True, null=True)
    brand = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    total_ratings = models.PositiveBigIntegerField(default=0)
    sum_ratings = models.PositiveIntegerField(default=0)  
    views = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            unique_slug = self.slug
            counter = 1
            if Product.objects.filter(slug=unique_slug).exists():
                unique_slug = f"{self.slug}-{counter}"
                counter +=1
            self.slug = unique_slug
        super().save(*args, **kwargs)
    
    @property
    def average_rating(self):
        if self.total_ratings == 0:
            return 0
        return self.sum_ratings / self.total_ratings

class Rating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()                               
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'user') 

    
    