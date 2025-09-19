from django.db import models
from django.conf import settings
from django.utils import timezone

# Create your models here.

class Novel(models.Model):
    """小说模型"""
    name = models.CharField(max_length=200, verbose_name='小说名称')
    author = models.CharField(max_length=100, verbose_name='作者')
    publisher = models.CharField(max_length=100, verbose_name='出版社')
    rank = models.IntegerField(default=0, verbose_name='排名')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='价格')
    year = models.CharField(max_length=4, default='2025', verbose_name='年份')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '小说'
        verbose_name_plural = '小说列表'
        ordering = ['rank']

class Cart(models.Model):
    """购物车模型"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='cart',
        verbose_name='用户'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name='会话键')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        if self.user:
            return f"{self.user.username}的购物车"
        return f"匿名购物车 (会话: {self.session_key})"
    
    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车列表'

class CartItem(models.Model):
    """购物车项目模型"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='购物车'
    )
    novel = models.ForeignKey(
        Novel,
        on_delete=models.CASCADE,
        verbose_name='小说'
    )
    quantity = models.IntegerField(default=1, verbose_name='数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def __str__(self):
        return f"{self.novel.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        """计算商品小计"""
        return self.novel.price * self.quantity
    
    class Meta:
        verbose_name = '购物车项目'
        verbose_name_plural = '购物车项目列表'
        unique_together = ('cart', 'novel')  # 确保每个购物车中同一商品只出现一次
