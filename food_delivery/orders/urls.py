# orders/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RestaurantViewSet, OrderViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'restaurants', RestaurantViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
