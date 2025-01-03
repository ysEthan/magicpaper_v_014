from django.contrib import admin
from .models import Brand, Category, SPU, SKU

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_at', 'updated_at')
    list_filter = ('status',)
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name_zh', 'category_name_en', 'level', 'parent',
                   'rank_id', 'is_last_level', 'status', 'created_at']
    list_filter = ['level', 'is_last_level', 'status']
    search_fields = ['category_name_zh', 'category_name_en']
    list_editable = ['rank_id', 'status']
    raw_id_fields = ['parent']
    readonly_fields = ['created_at', 'updated_at']
    fieldsets = [
        (None, {
            'fields': [
                ('category_name_zh', 'category_name_en'),
                ('level', 'parent'),
                'description',
                'image',
                ('rank_id', 'is_last_level', 'status'),
                ('created_at', 'updated_at'),
            ]
        }),
    ]

@admin.register(SPU)
class SPUAdmin(admin.ModelAdmin):
    list_display = ('spu_code', 'spu_name', 'product_type', 'brand', 'category', 'status')
    list_filter = ('product_type', 'status', 'brand', 'category')
    search_fields = ('spu_code', 'spu_name')
    raw_id_fields = ('brand', 'category', 'poc')
    ordering = ('-created_at',)

@admin.register(SKU)
class SKUAdmin(admin.ModelAdmin):
    list_display = ('sku_code', 'sku_name', 'spu', 'material', 'color', 'status')
    list_filter = ('status', 'plating_process', 'surface_treatment')
    search_fields = ('sku_code', 'sku_name', 'material', 'color')
    raw_id_fields = ('spu',)
    ordering = ('-created_at',)
