# orders/tasks.py

from celery import shared_task
from .models import Order, Payment
import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY

@shared_task
def process_payment(order_id):
    order = Order.objects.get(id=order_id)

    # Here we would call Stripe to process the payment
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=int(order.total_price * 100),  # Convert to cents
            currency='usd',
            payment_method_types=['card'],
        )

        # Save the payment information
        payment = Payment.objects.create(
            order=order,
            stripe_payment_id=payment_intent.id,
            status='success',
            amount=order.total_price,
        )

        # Update the order status to completed
        order.status = 'completed'
        order.save()

    except stripe.error.StripeError as e:
        # Handle payment failure
        payment = Payment.objects.create(
            order=order,
            status='failed',
            amount=order.total_price,
        )
        order.status = 'failed'
        order.save()

    return f"Payment processed for order {order_id}"
