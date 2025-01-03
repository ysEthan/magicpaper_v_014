from django.urls import path
from . import views

app_name = 'procurement'

urlpatterns = [
    # 供应商管理URLs
    path('suppliers/', views.SupplierListView.as_view(), name='supplier-list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier-create'),
    path('suppliers/<int:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier-update'),
    path('suppliers/<int:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier-delete'),
    
    # 采购单管理URLs
    path('purchase-orders/', views.PurchaseOrderListView.as_view(), name='purchase-order-list'),
    path('purchase-orders/create/', views.PurchaseOrderCreateView.as_view(), name='purchase-order-create'),
    path('purchase-orders/<int:pk>/update/', views.PurchaseOrderUpdateView.as_view(), name='purchase-order-update'),
    path('purchase-orders/<int:pk>/detail/', views.PurchaseOrderDetailView.as_view(), name='purchase-order-detail'),
    
    # 采购单同步URL
    path('purchase-orders/sync/', views.sync_purchase_orders, name='sync-purchase-orders'),
] 