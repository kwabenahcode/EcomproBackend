# payments/views.py

from django.shortcuts import redirect
from django.conf import settings
from rest_framework import generics, permissions
from rest_framework.response import Response
from decimal import Decimal
import uuid
import requests

from .models import Transaction
from Cart.models import Cart
from Orders.models import Order, OrderItem


PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_INITIALIZE_URL = "https://api.paystack.co/transaction/initialize"
PAYSTACK_VERIFY_URL = "https://api.paystack.co/transaction/verify/"


class InitiatePaymentAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            cart_code = request.data.get("cart_code")
            cart = Cart.objects.get(cart_code=cart_code)
            user = request.user

            amount = sum(
                item.quantity * item.product.price
                for item in cart.items.all()
            )

            tax = Decimal("4.00")
            total_amount = amount + tax

            reference = str(uuid.uuid4())

            transaction = Transaction.objects.create(
                ref=reference,
                cart=cart,
                user=user,
                amount=total_amount,
                currency="GHS",
                status="pending"
            )

            payload = {
                "email": user.email,
                "amount": int(total_amount * 100),
                "reference": reference,
                "callback_url": f"{settings.BASE_URL}/api/payment-callback/",
            }

            headers = {
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            response = requests.post(
                PAYSTACK_INITIALIZE_URL,
                json=payload,
                headers=headers
            ).json()

            if not response.get("status"):
                return Response(
                    {"error": response.get("message")},
                    status=400
                )

            return Response({
                "payment_url": response["data"]["authorization_url"],
                "reference": reference
            })

        except Cart.DoesNotExist:
            return Response({"error": "Invalid cart"}, status=400)

        except Exception as e:
            return Response({"error": str(e)}, status=500)

class PaymentCallbackAPI(generics.GenericAPIView):
    permission_classes = []

    def get(self, request):
        reference = request.GET.get("reference")

        if not reference:
            return redirect(f"{settings.FRONTEND_URL}/payment-status?error=invalid_reference")

        try:
            headers = {
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            }

            response = requests.get(
                f"{PAYSTACK_VERIFY_URL}{reference}",
                headers=headers
            ).json()

            if not response.get("status") or response["data"]["status"] != "success":
                return redirect(
                    f"{settings.FRONTEND_URL}/payment-status?error=verification_failed&reference={reference}"
                )

            transaction = Transaction.objects.get(ref=reference)

            # Prevent duplicate orders
            if transaction.status == "completed":
                return redirect(
                    f"{settings.FRONTEND_URL}/payment-status?reference={reference}"
                )

            cart = transaction.cart

            total_amount = sum(
                item.quantity * item.product.price
                for item in cart.items.all()
            ) + Decimal("4.00")

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

            return redirect(
                f"{settings.FRONTEND_URL}/payment-status?reference={reference}"
            )

        except Exception:
            return redirect(
                f"{settings.FRONTEND_URL}/payment-status?error=server_error&reference={reference}"
            )


class PaymentStatusAPI(generics.GenericAPIView):
    permission_classes = []

    def get(self, request):
        reference = request.GET.get("reference")

        if not reference:
            return Response({
                "message": "Payment Failed",
                "subMessage": "Invalid reference"
            }, status=400)

        try:
            transaction = Transaction.objects.get(ref=reference)

            if transaction.status == "completed":
                return Response({
                    "message": "Payment Successful",
                    "subMessage": "Your payment has been confirmed 🎉"
                })
            else:
                return Response({
                    "message": "Payment Pending",
                    "subMessage": "Payment is still processing"
                })

        except Transaction.DoesNotExist:
            return Response({
                "message": "Payment Failed",
                "subMessage": "Transaction not found"
            }, status=404)
