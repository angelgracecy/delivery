from django.shortcuts import render
# orders/views.py

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from .models import Restaurant, Order, Payment
from .serializers import RestaurantSerializer, OrderSerializer, PaymentSerializer
import stripe
from django.conf import settings
from .tasks import process_payment

stripe.api_key = settings.STRIPE_API_KEY

class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):
        # Create the order
        order_serializer = self.get_serializer(data=request.data)
        order_serializer.is_valid(raise_exception=True)
        order = order_serializer.save()

        # Call the background task to process payment
        process_payment.delay(order.id)

        return Response(order_serializer.data, status=201)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


# orders/views.py

@api_view(['POST'])
def create_payment(request, order_id):
    order = Order.objects.get(id=order_id)
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(order.total_price * 100),  # Convert to cents
            currency='usd',
        )
        return JsonResponse({"client_secret": payment_intent.client_secret})
    except stripe.error.StripeError as e:
        return JsonResponse({"error": str(e)}, status=400)
