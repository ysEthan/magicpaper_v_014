from django.urls import path
from . import views

app_name = 'logistics'

urlpatterns = [
    path('packages/', views.package_list, name='package_list'),
    path('packages/<int:package_id>/', views.package_detail, name='package_detail'),
    path('packages/create/<int:order_id>/', views.create_package, name='create_package'),
    path('packages/<int:package_id>/status/', views.update_package_status, name='update_package_status'),
    path('packages/<int:package_id>/label/', views.upload_shipping_label, name='upload_shipping_label'),
    path('packages/<int:package_id>/tracking/', views.update_tracking_info, name='update_tracking_info'),
] 