from django.contrib import admin
from .models import Shop, Order, Cart

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'platform', 'is_active', 'created_at')
    list_filter = ('platform', 'is_active')
    search_fields = ('name', 'code')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_no', 'platform_order_no', 'shop', 'order_type', 'status', 'paid_amount', 'created_at')
    list_filter = ('status', 'order_type', 'shop')
    search_fields = ('order_no', 'platform_order_no', 'recipient_name', 'recipient_phone')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('order', 'sku', 'qty', 'price', 'actual_price', 'is_out_of_stock')
    list_filter = ('is_out_of_stock',)
    search_fields = ('order__order_no', 'sku__sku_code')
