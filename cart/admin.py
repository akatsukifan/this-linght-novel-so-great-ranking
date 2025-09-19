from django.contrib import admin
from .models import Novel, Cart, CartItem

class NovelAdmin(admin.ModelAdmin):
    """小说模型的管理界面配置"""
    list_display = ('name', 'author', 'publisher', 'rank', 'price', 'created_at')
    list_filter = ('author', 'publisher', 'created_at')
    search_fields = ('name', 'author', 'publisher')
    ordering = ('rank', 'created_at')
    list_editable = ('rank', 'price')
    
    fieldsets = (
        ('基本信息', {
            'fields': ('name', 'author', 'publisher', 'rank', 'price')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')

class CartItemInline(admin.TabularInline):
    """购物车项目的内联显示"""
    model = CartItem
    extra = 1
    fields = ('novel', 'quantity', 'subtotal')
    readonly_fields = ('subtotal',)
    ordering = ('novel__name',)
    
    def subtotal(self, obj):
        """显示商品小计"""
        return obj.subtotal
    subtotal.short_description = '小计'

class CartAdmin(admin.ModelAdmin):
    """购物车模型的管理界面配置"""
    list_display = ('__str__', 'user', 'session_key', 'total_items', 'total_amount', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'session_key')
    ordering = ('-updated_at',)
    inlines = [CartItemInline]
    
    fieldsets = (
        ('购物车信息', {
            'fields': ('user', 'session_key')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def total_items(self, obj):
        """显示购物车中的商品总数"""
        return sum(item.quantity for item in obj.items.all())
    total_items.short_description = '商品总数'
    
    def total_amount(self, obj):
        """显示购物车中的总金额"""
        return sum(item.subtotal for item in obj.items.all())
    total_amount.short_description = '总金额'
    total_amount.admin_order_field = 'total_amount'

class CartItemAdmin(admin.ModelAdmin):
    """购物车项目模型的管理界面配置"""
    list_display = ('novel', 'cart', 'quantity', 'subtotal', 'created_at')
    list_filter = ('cart', 'novel', 'created_at')
    search_fields = ('novel__name', 'cart__user__username')
    ordering = ('cart', 'novel__name')
    
    fieldsets = (
        ('购物车项目信息', {
            'fields': ('cart', 'novel', 'quantity')
        }),
        ('时间信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def subtotal(self, obj):
        """显示商品小计"""
        return obj.subtotal
    subtotal.short_description = '小计'

# 注册模型到管理界面
admin.site.register(Novel, NovelAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartItem, CartItemAdmin)
