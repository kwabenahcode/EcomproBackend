from django.shortcuts import render
from .models import *
from User.models import *
from Cart.models import *
from Orders.models import *
from django.conf import settings 
from rest_framework import generics, permissions
from decimal import Decimal

import uuid


from rest_framework.response import Response
import requests

# Create your views here.
PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_INITIALIZE_URL = "https://api.paystack.co/transaction/initialize"
BASE_URL = settings.BASE_URL

class InitiatePaymentAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            cart_code = request.data.get("cart_code")
            cart = Cart.objects.get(cart_code=cart_code)
            user = request.user

            amount = sum([item.quantity * item.product.price for item in cart.items.all()])
            tax = Decimal("4.00")
            total_amount = amount + tax

            currency = "GHS"

            ref = str(uuid.uuid4())

            transaction = Transaction.objects.create(
            ref=ref,
            cart=cart,
            amount=total_amount,
            currency=currency,
            user=user,
            status="pending"
            )
            paystack_amount = int(total_amount * 100)

            payload = {
            "email": user.email,
            "amount": paystack_amount,
            "reference": ref,
            "callback_url": f"{BASE_URL}payment-status/",
            }

            headers = {
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            response = requests.post(PAYSTACK_INITIALIZE_URL, json=payload, headers=headers)
            res_data = response.json()

            if not res_data.get("status"):
                return Response({"error": res_data.get("message")}, status=400)

            print(res_data)
            
            return Response({
                "payment_url": res_data["data"]["authorization_url"],
                "reference": ref,
                "message": "success"
            })

        except Cart.DoesNotExist:
            return Response({"error": "Invalid Cart Code"}, status=400)

        except Exception as e:
            print("ERROR:", e)
            return Response({"error": str(e)}, status=500)

class PaymentCallBackAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        reference = request.GET.get("reference")
        user = request.user

        headers = {
            "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        }

        url = f"https://api.paystack.co/transaction/verify/{reference}"
        res = requests.get(url, headers=headers).json()

        if res["data"]["status"] != "success":
            return Response({"message": "Payment verification failed"}, status=400)

        transaction = Transaction.objects.get(ref=reference)

        # 🔐 STOP DUPLICATES
        if Order.objects.filter(transaction=transaction).exists():
            return Response({"message": "Order already created"})

        cart = transaction.cart

        amount = sum(item.quantity * item.product.price for item in cart.items.all())
        tax = Decimal("4.00")
        total_amount = amount + tax

        transaction.status = "completed"
        transaction.save()

        order = Order.objects.create(
            user=user,
            transaction=transaction,
            order_id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
            total_amount=total_amount,
            status="completed"
        )

        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart.items.all().delete()

        return Response({
            "message": "Payment Successful",
            "subMessage": "Your payment has been confirmed 🎉"
        })
