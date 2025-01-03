from django.contrib import admin
from .models import Carrier, Service, Package

@admin.register(Carrier)
class CarrierAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'website', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'code')
    ordering = ('name',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('carrier', 'name', 'code', 'estimated_days', 'base_fee', 'is_active')
    list_filter = ('carrier', 'is_active')
    search_fields = ('name', 'code')
    ordering = ('carrier', 'name')

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('order', 'warehouse', 'service', 'tracking_no', 'status', 'shipping_fee', 'shipped_at')
    list_filter = ('status', 'warehouse', 'service__carrier')
    search_fields = ('order__order_no', 'tracking_no')
    raw_id_fields = ('order',)
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('基本信息', {
            'fields': ('order', 'warehouse', 'service', 'tracking_no', 'status')
        }),
        ('包裹信息', {
            'fields': ('shipping_fee', 'weight', 'length', 'width', 'height', 'items')
        }),
        ('物流信息', {
            'fields': ('shipping_label', 'shipped_at', 'delivered_at', 'tracking_info')
        }),
        ('系统信息', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
