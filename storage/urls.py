from django.urls import path
from . import views

app_name = 'storage'

urlpatterns = [
    # 仓库管理URLs
    path('warehouses/', views.WarehouseListView.as_view(), name='warehouse-list'),
    path('warehouses/create/', views.WarehouseCreateView.as_view(), name='warehouse-create'),
    path('warehouses/<int:pk>/update/', views.WarehouseUpdateView.as_view(), name='warehouse-update'),
    path('warehouses/<int:pk>/delete/', views.WarehouseDeleteView.as_view(), name='warehouse-delete'),
    
    # 货位管理URLs
    path('allocations/', views.AllocationListView.as_view(), name='allocation-list'),
    path('allocations/create/', views.AllocationCreateView.as_view(), name='allocation-create'),
    path('allocations/<int:pk>/update/', views.AllocationUpdateView.as_view(), name='allocation-update'),
    path('allocations/<int:pk>/delete/', views.AllocationDeleteView.as_view(), name='allocation-delete'),
    
    # 库存管理URLs
    path('stocks/', views.StockListView.as_view(), name='stock-list'),
    
    # 入库管理URLs
    path('stock-in/', views.StockInRecordListView.as_view(), name='stock-in-list'),
    path('stock-in/create/', views.StockInRecordCreateView.as_view(), name='stock-in-create'),
    path('stock-in/<int:pk>/', views.StockInRecordDetailView.as_view(), name='stock-in-detail'),
    path('stock-in/<int:pk>/add-detail/', views.stock_in_add_detail, name='stock-in-add-detail'),
    path('stock-in/<int:pk>/delete-detail/<int:detail_pk>/', views.stock_in_delete_detail, name='stock-in-delete-detail'),
    
    # 出库管理URLs
    path('stock-out/', views.StockOutRecordListView.as_view(), name='stock-out-list'),
    path('stock-out/create/', views.StockOutRecordCreateView.as_view(), name='stock-out-create'),
    path('stock-out/<int:pk>/', views.StockOutRecordDetailView.as_view(), name='stock-out-detail'),
    path('stock-out/<int:pk>/add-detail/', views.stock_out_add_detail, name='stock-out-add-detail'),
    path('stock-out/<int:pk>/delete-detail/<int:detail_pk>/', views.stock_out_delete_detail, name='stock-out-delete-detail'),
] 