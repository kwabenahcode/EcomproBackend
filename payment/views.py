from django.shortcuts import render, redirect  # Make sure redirect is imported
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
                "callback_url": f"{BASE_URL}/api/payment-status/",
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
    permission_classes = []

    def get(self, request, *args, **kwargs):
        try:
            reference = request.GET.get("reference")
            
            # If this is an API call from React (not a Paystack redirect)
            if request.headers.get('Accept') == 'application/json' or 'api' in request.path:
                # Return JSON for React to consume
                transaction = Transaction.objects.get(ref=reference)
                order = Order.objects.filter(transaction=transaction).first()
                
                if order:
                    return Response({
                        "message": "Payment Successful",
                        "subMessage": "Your payment has been confirmed 🎉"
                    })
                else:
                    return Response({
                        "message": "Payment Pending",
                        "subMessage": "Payment received but order is being processed"
                    })
            
            # Otherwise, this is a Paystack redirect - do the full verification and redirect
            headers = {
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            }

            url = f"https://api.paystack.co/transaction/verify/{reference}"
            res = requests.get(url, headers=headers).json()

            if res["data"]["status"] != "success":
                return redirect(f"{settings.FRONTEND_URL}/payment-status?error=verification_failed&reference={reference}")

            transaction = Transaction.objects.get(ref=reference)
            order = Order.objects.filter(transaction=transaction).first()

            if not order:
                cart = transaction.cart
                amount = sum(item.quantity * item.product.price for item in cart.items.all())
                tax = Decimal("4.00")
                total_amount = amount + tax

                transaction.status = "completed"
                transaction.save()

                order = Order.objects.create(
                    user=transaction.user,
                    transaction=transaction,
                    order_id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
                    total_amount=total_amount,
                    status="paid"
                )

                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )

                cart.items.all().delete()

            # Redirect to frontend with just the reference
            return redirect(f"{settings.FRONTEND_URL}/payment-status?reference={reference}")

        except Exception as e:
            print(f"Error in payment callback: {e}")
            return redirect(f"{settings.FRONTEND_URL}/payment-status?error={str(e)}&reference={reference if 'reference' in locals() else ''}")