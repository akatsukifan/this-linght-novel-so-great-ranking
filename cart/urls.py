from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NovelViewSet, CartViewSet, AuthViewSet

router = DefaultRouter()
router.register(r'novels', NovelViewSet, basename='novel')
router.register(r'cart', CartViewSet, basename='cart')
router.register(r'auth', AuthViewSet, basename='auth')

urlpatterns = [
    path('', include(router.urls)),
]