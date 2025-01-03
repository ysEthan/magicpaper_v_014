from django.urls import path
from . import views

app_name = 'trade'

urlpatterns = [
    path('orders/', views.order_list, name='order_list'),
    path('orders/create/', views.create_order, name='create_order'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/process/', views.process_order, name='process_order'),
    path('orders/<int:order_id>/ship/', views.ship_order, name='ship_order'),
    path('orders/<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('orders/sync/', views.sync_orders, name='sync_orders'),
    path('api/parse-address/', views.parse_address, name='parse_address'),
    path('api/search-sku/', views.search_sku, name='search_sku'),
] 