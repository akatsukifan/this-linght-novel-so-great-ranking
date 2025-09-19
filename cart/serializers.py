from rest_framework import serializers
from .models import Novel, Cart, CartItem
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class NovelSerializer(serializers.ModelSerializer):
    """小说序列化器"""
    class Meta:
        model = Novel
        fields = ['id', 'name', 'author', 'publisher', 'rank', 'price', 'year']

class CartItemSerializer(serializers.ModelSerializer):
    """购物车项目序列化器"""
    novel = NovelSerializer(read_only=True)
    novel_id = serializers.PrimaryKeyRelatedField(queryset=Novel.objects.all(), write_only=True, source='novel')
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'novel', 'novel_id', 'quantity', 'subtotal']
        read_only_fields = ['id', 'novel', 'subtotal']

class CartSerializer(serializers.ModelSerializer):
    """购物车序列化器"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_items', 'total_amount', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'items', 'total_items', 'total_amount', 'created_at', 'updated_at']
    
    def to_representation(self, instance):
        """自定义序列化输出，计算总数和总金额"""
        representation = super().to_representation(instance)
        # 计算购物车中的商品总数
        items = instance.items.all()
        total_items = sum(item.quantity for item in items)
        total_amount = sum(item.subtotal for item in items)
        
        representation['total_items'] = total_items
        representation['total_amount'] = total_amount
        return representation