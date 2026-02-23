from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.conf import settings
from decimal import Decimal
from Cart.models import *
from .models import Transaction
from Orders.models import *
from django.shortcuts import redirect

import uuid
import requests


PAYSTACK_SECRET_KEY = settings.PAYSTACK_SECRET_KEY
PAYSTACK_INITIALIZE_URL = "https://api.paystack.co/transaction/initialize"

class InitiatePaymentAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            cart_code = request.data.get("cart_code")
            if not cart_code:
                return Response({"error": "cart_code is required"}, status=status.HTTP_400_BAD_REQUEST)

            cart = Cart.objects.get(cart_code=cart_code)
            user = request.user

            amount = sum(item.quantity * item.product.price for item in cart.items.all())
            tax = Decimal("4.00")
            total_amount = amount + tax

            currency = "GHS"
            ref = str(uuid.uuid4())

            Transaction.objects.create(
                ref=ref,
                cart=cart,
                amount=total_amount,
                currency=currency,
                user=user,
                status="pending"
            )

            paystack_amount = int(total_amount * 100)

            # ✅ IMPORTANT: This is the Paystack redirect callback endpoint (AllowAny)
            callback_url = f"{settings.BASE_URL}/api/payment_callback/"

            payload = {
                "email": user.email,
                "amount": paystack_amount,
                "reference": ref,
                "callback_url": callback_url,
                "currency": currency,
            }

            headers = {
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
                "Content-Type": "application/json",
            }

            response = requests.post(PAYSTACK_INITIALIZE_URL, json=payload, headers=headers)
            res_data = response.json()

            if not res_data.get("status"):
                return Response({"error": res_data.get("message")}, status=status.HTTP_400_BAD_REQUEST)

            return Response({
                "payment_url": res_data["data"]["authorization_url"],
                "reference": ref,
                "message": "success"
            })

        except Cart.DoesNotExist:
            return Response({"error": "Invalid Cart Code"}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentCallBackAPI(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            reference = request.GET.get("reference")
            trxref = request.GET.get("trxref")  # Paystack also sends this

            headers = {
                "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
            }

            url = f"https://api.paystack.co/transaction/verify/{reference}"
            res = requests.get(url, headers=headers).json()

            # Get frontend URL from settings or use default
            frontend_url = getattr(settings, 'FRONTEND_URL', 'https://ecompro-online.vercel.app')

            if res["data"]["status"] != "success":
                # Redirect to frontend with error
                return redirect(
                    f"{frontend_url}/payment-status?"
                    f"error=verification_failed&"
                    f"reference={reference}"
                )

            transaction = Transaction.objects.get(ref=reference)

            order = Order.objects.filter(transaction=transaction).first()

            if order:
                # Order already exists, redirect to success page
                return redirect(
                    f"{frontend_url}/payment-status?"
                    f"reference={reference}&"
                    f"order_id={order.order_id}&"
                    f"amount={order.total_amount}&"
                    f"status=already_confirmed"
                )

            cart = transaction.cart

            amount = sum(
                item.quantity * item.product.price
                for item in cart.items.all()
            )
            tax = Decimal("4.00")
            total_amount = amount + tax

            transaction.status = "completed"
            transaction.save()

            order, created = Order.objects.get_or_create(
                user=transaction.user,
                transaction=transaction,
                order_id=f"ORD-{uuid.uuid4().hex[:8].upper()}",
                total_amount=total_amount,
                status="paid"
            )

            if created:
                for item in cart.items.all():
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        quantity=item.quantity,
                        price=item.product.price
                    )

                cart.items.all().delete()

            # Redirect to frontend success page
            return redirect(
                f"{frontend_url}/payment-status?"
                f"reference={reference}&"
                f"order_id={order.order_id}&"
                f"amount={total_amount}"
            )

        except Transaction.DoesNotExist:
            print(f"Transaction not found for reference: {reference}")
            frontend_url = getattr(settings, 'FRONTEND_URL', 'https://ecompro-online.vercel.app')
            return redirect(
                f"{frontend_url}/payment-status?"
                f"error=transaction_not_found&"
                f"reference={reference}"
            )

        except Exception as e:
            print(f"Error in payment callback: {e}")
            frontend_url = getattr(settings, 'FRONTEND_URL', 'https://ecompro-online.vercel.app')
            return redirect(
                f"{frontend_url}/payment-status?"
                f"error={str(e)}&"
                f"reference={reference if 'reference' in locals() else ''}"
            )
        
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
import requests
from django.conf import settings

class PaymentStatusAPI(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        reference = request.GET.get("reference")
        if not reference:
            return Response({"message": "Missing reference"}, status=status.HTTP_400_BAD_REQUEST)

        headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        res = requests.get(url, headers=headers).json()

        if not res.get("status"):
            return Response({"message": "Paystack verification error"}, status=status.HTTP_400_BAD_REQUEST)

        paystack_status = res["data"]["status"]

        try:
            transaction = Transaction.objects.get(ref=reference, user=request.user)
        except Transaction.DoesNotExist:
            return Response({"message": "Transaction not found"}, status=status.HTTP_404_NOT_FOUND)

        order = Order.objects.filter(transaction=transaction).first()

        if paystack_status == "success" and order:
            return Response({
                "message": "Payment Successful",
                "order_id": order.order_id,
                "amount": str(order.total_amount),
            })

        return Response({
            "message": "Payment Not Successful",
            "paystack_status": paystack_status,
        }, status=status.HTTP_400_BAD_REQUEST)
