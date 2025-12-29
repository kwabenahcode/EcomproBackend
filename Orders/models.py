from django.db import models
from django.conf import settings
from User.models import *
from Cart.models import *
from payment.models import *

# Create your models here.
class Order(models.Model):
    order_id = models.CharField(max_length=20, unique=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    transaction = models.OneToOneField(
        Transaction,
        on_delete=models.CASCADE,
        related_name="order"
    )
    total_amount = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("paid", "Paid"),
            ("pending", "Pending"),
            ("delivered", "Delivered"),
        ],
        default="paid"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.order_id
    


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="orderitems",
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(decimal_places=2, max_digits=10, blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} ({self.order.order_id})"
