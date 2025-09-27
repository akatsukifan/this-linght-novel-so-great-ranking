from django.contrib import admin
from .models import Novel, Cart, CartItem

class NovelAdmin(admin.ModelAdmin):
    """小説モデルの管理インターフェース設定"""
    list_display = ('name', 'author', 'publisher', 'rank', 'price', 'created_at')
    list_filter = ('author', 'publisher', 'created_at')
    search_fields = ('name', 'author', 'publisher')
    ordering = ('rank', 'created_at')
    list_editable = ('rank', 'price')
    
    fieldsets = (
        ('基本情報', {
            'fields': ('name', 'author', 'publisher', 'rank', 'price')
        }),
        ('時間情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

class CartItemInline(admin.TabularInline):
    """カートアイテムのインライン表示"""
    model = CartItem
    extra = 1
    fields = ('novel', 'quantity', 'subtotal')
    readonly_fields = ('subtotal',)
    ordering = ('novel__name',)
    
    def subtotal(self, obj):
        """商品小計を表示"""
        return obj.subtotal
    subtotal.short_description = '小計'

class CartAdmin(admin.ModelAdmin):
    """カートモデルの管理インターフェース設定"""
    list_display = ('__str__', 'user', 'session_key', 'total_items', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'session_key')
    ordering = ('-updated_at',)
    inlines = [CartItemInline]
    
    fieldsets = (
        ('カート情報', {
            'fields': ('user', 'session_key')
        }),
        ('時間情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def total_items(self, obj):
        """カート内の商品総数を表示"""
        return sum(item.quantity for item in obj.items.all())
    total_items.short_description = '商品総数'
    
    def total_amount(self, obj):
        """カート内の総金額を表示"""
        return sum(item.subtotal for item in obj.items.all())
    total_amount.short_description = '総金額'
    total_amount.admin_order_field = 'total_amount'

class CartItemAdmin(admin.ModelAdmin):
    """カートアイテムモデルの管理インターフェース設定"""
    list_display = ('novel', 'cart', 'quantity', 'subtotal', 'created_at')
    list_filter = ('cart', 'novel', 'created_at')
    search_fields = ('novel__name', 'cart__user__username')
    ordering = ('cart', 'novel__name')
    
    fieldsets = (
        ('カートアイテム情報', {
            'fields': ('cart', 'novel', 'quantity')
        }),
        ('時間情報', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def subtotal(self, obj):
        """商品小計を表示"""
        return obj.subtotal
    subtotal.short_description = '小計'

# モデルを管理サイトに登録
admin.site.register(Novel, NovelAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
