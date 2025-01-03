from django.urls import path
from . import views

app_name = 'manufacturing'

urlpatterns = [
    # 工厂管理
    path('factories/', views.factory_list, name='factory_list'),
    path('factories/create/', views.factory_create, name='factory_create'),
    path('factories/<int:pk>/edit/', views.factory_edit, name='factory_edit'),
    
    # 生产订单管理
    path('orders/', views.production_order_list, name='production_order_list'),
    path('orders/create/', views.production_order_create, name='production_order_create'),
    path('orders/<int:pk>/edit/', views.production_order_edit, name='production_order_edit'),
    
    # 样品评审管理
    path('orders/<int:order_id>/reviews/', views.sample_review_list, name='sample_review_list'),
    path('orders/<int:order_id>/reviews/create/', views.sample_review_create, name='sample_review_create'),
] 