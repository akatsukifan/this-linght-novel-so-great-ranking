from django.db import models
from django.conf import settings
from django.utils import timezone

# モデルを作成

class Novel(models.Model):
    """小説モデル"""
    name = models.CharField(max_length=200, verbose_name='小説名')
    author = models.CharField(max_length=100, verbose_name='作者')
    publisher = models.CharField(max_length=100, verbose_name='出版社')
    rank = models.IntegerField(default=0, verbose_name='ランキング')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='価格')
    year = models.CharField(max_length=4, default='2025', verbose_name='年')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = '小説'
        verbose_name_plural = '小説リスト'
        ordering = ['rank']

class Cart(models.Model):
    """カートモデル"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='cart',
        verbose_name='ユーザー'
    )
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name='セッションキー')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    def __str__(self):
        if self.user:
            return f"{self.user.username}のカート"
        return f"匿名カート (セッション: {self.session_key})"
    
    class Meta:
        verbose_name = 'カート'
        verbose_name_plural = 'カートリスト'

class CartItem(models.Model):
    """カートアイテムモデル"""
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='カート'
    )
    novel = models.ForeignKey(
        Novel,
        on_delete=models.CASCADE,
        verbose_name='小説'
    )
    quantity = models.IntegerField(default=1, verbose_name='数量')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='作成日時')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新日時')
    
    def __str__(self):
        return f"{self.novel.name} x {self.quantity}"
    
    @property
    def subtotal(self):
        """商品の小計を計算"""
        return self.novel.price * self.quantity
    
    class Meta:
        verbose_name = 'カートアイテム'
        verbose_name_plural = 'カートアイテムリスト'
        unique_together = ('cart', 'novel')  # 各カート内で同じ商品が1回のみ出現するようにする
