from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from .models import Package, Service, Carrier, PackageStatusLog
from trade.models import Order

@login_required
def package_list(request):
    """包裹列表视图"""
    packages = Package.objects.all()
    
    # 筛选条件
    status = request.GET.get('status')
    warehouse_id = request.GET.get('warehouse')
    carrier_id = request.GET.get('carrier')
    tracking_no = request.GET.get('tracking_no')
    order_no = request.GET.get('order_no')
    
    if status:
        packages = packages.filter(status=status)
    if warehouse_id:
        packages = packages.filter(warehouse_id=warehouse_id)
    if carrier_id:
        packages = packages.filter(service__carrier_id=carrier_id)
    if tracking_no:
        packages = packages.filter(tracking_no__icontains=tracking_no)
    if order_no:
        packages = packages.filter(order__order_no__icontains=order_no)
    
    # 分页
    paginator = Paginator(packages, 20)
    page = request.GET.get('page')
    packages = paginator.get_page(page)
    
    context = {
        'packages': packages,
        'package_statuses': Package.PackageStatus.choices
    }
    return render(request, 'logistics/package_list.html', context)

@login_required
def package_detail(request, package_id):
    """包裹详情视图"""
    package = get_object_or_404(Package, id=package_id)
    context = {
        'package': package
    }
    return render(request, 'logistics/package_detail.html', context)

@login_required
def create_package(request, order_id):
    """创建包裹视图"""
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        try:
            # 创建包裹
            package = Package.objects.create(
                order=order,
                warehouse_id=request.POST.get('warehouse'),
                service_id=request.POST.get('service'),
                tracking_no=request.POST.get('tracking_no', ''),
                shipping_fee=request.POST.get('shipping_fee', 0),
                weight=request.POST.get('weight', 0),
                length=request.POST.get('length', 0),
                width=request.POST.get('width', 0),
                height=request.POST.get('height', 0),
                items=order.cart_set.values('sku__sku_code', 'sku__sku_name', 'qty')
            )
            
            messages.success(request, '包裹创建成功')
            return redirect('logistics:package_detail', package_id=package.id)
            
        except Exception as e:
            messages.error(request, f'包裹创建失败：{str(e)}')
            return redirect('logistics:create_package', order_id=order_id)
    
    context = {
        'order': order,
        'services': Service.objects.filter(is_active=True)
    }
    return render(request, 'logistics/package_form.html', context)

@login_required
def update_package_status(request, package_id):
    """更新包裹状态"""
    if request.method == 'POST':
        package = get_object_or_404(Package, id=package_id)
        status = request.POST.get('status')
        remark = request.POST.get('remark', '')
        
        if status in dict(Package.PackageStatus.choices):
            with transaction.atomic():
                # 记录原状态
                old_status = package.status
                
                # 更新包裹状态
                package.status = status
                if status == Package.PackageStatus.SHIPPED:
                    package.shipped_at = timezone.now()
                elif status == Package.PackageStatus.DELIVERED:
                    package.delivered_at = timezone.now()
                package.save()
                
                # 创建状态变更记录
                PackageStatusLog.objects.create(
                    package=package,
                    from_status=old_status,
                    to_status=status,
                    remark=remark,
                    operator=request.user
                )
            
            messages.success(request, '包裹状态更新成功')
        else:
            messages.error(request, '无效的状态值')
            
    return redirect('logistics:package_detail', package_id=package_id)

@login_required
def upload_shipping_label(request, package_id):
    """上传物流面单"""
    if request.method == 'POST' and request.FILES.get('shipping_label'):
        package = get_object_or_404(Package, id=package_id)
        package.shipping_label = request.FILES['shipping_label']
        package.save()
        messages.success(request, '面单上传成功')
    return redirect('logistics:package_detail', package_id=package_id)

@login_required
def update_tracking_info(request, package_id):
    """更新物流跟踪信息"""
    if request.method == 'POST':
        try:
            package = get_object_or_404(Package, id=package_id)
            tracking_info = request.POST.get('tracking_info', '[]')
            package.tracking_info = tracking_info
            package.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
