from django.urls import path
from . import views

app_name = 'gallery'

urlpatterns = [
    path('brands/', views.brand_list, name='brand_list'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('spus/', views.spu_list, name='spu_list'),
    path('spus/create/', views.spu_create, name='spu_create'),
    path('spus/<int:pk>/edit/', views.spu_edit, name='spu_edit'),
    path('spus/<int:pk>/delete/', views.spu_delete, name='spu_delete'),
    path('skus/', views.sku_list, name='sku_list'),
    path('skus/create/', views.sku_create, name='sku_create'),
    path('skus/<int:pk>/edit/', views.sku_edit, name='sku_edit'),
    path('skus/<int:pk>/delete/', views.sku_delete, name='sku_delete'),
    path('skus/<str:sku_code>/', views.sku_detail, name='sku_detail'),
] 