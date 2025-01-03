from django.contrib import admin
from .models import Factory, ProductionOrder, SampleReview

@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'contact', 'phone', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'code', 'contact']
    ordering = ['-created_at']

@admin.register(ProductionOrder)
class ProductionOrderAdmin(admin.ModelAdmin):
    list_display = ['order_no', 'order_type', 'sku', 'factory', 'quantity', 'status', 'follower', 'created_at']
    list_filter = ['order_type', 'status', 'factory']
    search_fields = ['order_no', 'sku__sku_code', 'factory__name']
    ordering = ['-created_at']
    raw_id_fields = ['sku', 'factory', 'creator', 'follower']

@admin.register(SampleReview)
class SampleReviewAdmin(admin.ModelAdmin):
    list_display = ['production_order', 'reviewer', 'review_date', 'conclusion', 'created_at']
    list_filter = ['review_date', 'reviewer']
    search_fields = ['production_order__order_no', 'conclusion', 'content']
    ordering = ['-review_date']
    raw_id_fields = ['production_order', 'reviewer']
