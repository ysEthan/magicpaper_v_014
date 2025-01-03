from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
from .models import Shop, Order, Cart
from gallery.models import SKU
from storage.models import Warehouse
from logistics.models import Service, Package
import json
import re

@login_required
def order_list(request):
    """订单列表视图"""
    orders = Order.objects.all()
    
    # 筛选条件
    shop_id = request.GET.get('shop')
    status = request.GET.get('status')
    order_no = request.GET.get('order_no')
    recipient_name = request.GET.get('recipient_name')
    recipient_phone = request.GET.get('recipient_phone')
    
    if shop_id:
        orders = orders.filter(shop_id=shop_id)
    if status:
        orders = orders.filter(status=status)
    if order_no:
        orders = orders.filter(order_no__icontains=order_no)
    if recipient_name:
        orders = orders.filter(recipient_name__icontains=recipient_name)
    if recipient_phone:
        orders = orders.filter(recipient_phone__icontains=recipient_phone)
    
    # 分页
    paginator = Paginator(orders, 20)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'shops': Shop.objects.filter(is_active=True),
        'order_statuses': Order.OrderStatus.choices
    }
    return render(request, 'trade/order_list.html', context)

@login_required
def order_detail(request, order_id):
    """订单详情视图"""
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
        'cart_items': order.cart_set.all()
    }
    return render(request, 'trade/order_detail.html', context)

def generate_order_no():
    """生成订单号"""
    prefix = timezone.now().strftime('%Y%m%d')
    # 获取当天最后一个订单号
    last_order = Order.objects.filter(order_no__startswith=prefix).order_by('-order_no').first()
    if last_order:
        # 提取序号并加1
        seq = int(last_order.order_no[-4:]) + 1
    else:
        seq = 1
    return f"{prefix}{seq:04d}"

@login_required
def create_order(request):
    """创建订单视图"""
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 创建订单
                order = Order.objects.create(
                    shop_id=request.POST.get('shop'),
                    order_no=request.POST.get('order_no') or generate_order_no(),
                    recipient_name=request.POST.get('recipient_name'),
                    recipient_phone=request.POST.get('recipient_phone'),
                    recipient_email=request.POST.get('recipient_email'),
                    recipient_country=request.POST.get('recipient_country'),
                    recipient_state=request.POST.get('recipient_state'),
                    recipient_city=request.POST.get('recipient_city'),
                    recipient_address=request.POST.get('recipient_address'),
                    recipient_postcode=request.POST.get('recipient_postcode'),
                    status=Order.OrderStatus.PENDING,
                    created_at=timezone.now()
                )
                
                # 创建订单项
                cart_items = json.loads(request.POST.get('cart_items', '[]'))
                total_amount = 0
                for item in cart_items:
                    sku = SKU.objects.get(id=item['sku'])
                    price = float(item['price'])
                    qty = int(item['qty'])
                    Cart.objects.create(
                        order=order,
                        sku=sku,
                        qty=qty,
                        price=price,
                        actual_price=price,
                        cost=sku.cost_price
                    )
                    total_amount += price * qty
                
                # 更新订单总金额
                order.paid_amount = total_amount
                order.save()
                
                messages.success(request, '订单创建成功')
                return redirect('trade:order_detail', order_id=order.id)
        except Exception as e:
            messages.error(request, f'订单创建失败：{str(e)}')
            return redirect('trade:create_order')
    
    context = {
        'shops': Shop.objects.filter(is_active=True)
    }
    return render(request, 'trade/order_form.html', context)

@login_required
def process_order(request, order_id):
    """开始处理订单"""
    order = get_object_or_404(Order, id=order_id)
    if order.status == Order.OrderStatus.PENDING:
        order.status = Order.OrderStatus.PROCESSING
        order.save()
        messages.success(request, '订单已开始处理')
    else:
        messages.error(request, '订单状态不正确')
    return redirect('trade:order_detail', order_id=order_id)

@login_required
def ship_order(request, order_id):
    """标记订单为已发货"""
    order = get_object_or_404(Order, id=order_id)
    if order.status == Order.OrderStatus.PROCESSING:
        order.status = Order.OrderStatus.SHIPPED
        order.save()
        messages.success(request, '订单已标记为发货')
    else:
        messages.error(request, '订单状态不正确')
    return redirect('trade:order_detail', order_id=order_id)

@login_required
def cancel_order(request, order_id):
    """取消订单"""
    order = get_object_or_404(Order, id=order_id)
    if order.status not in [Order.OrderStatus.SHIPPED, Order.OrderStatus.COMPLETED]:
        order.status = Order.OrderStatus.CANCELLED
        order.save()
        messages.success(request, '订单已取消')
    else:
        messages.error(request, '已发货或已完成的订单不能取消')
    return redirect('trade:order_detail', order_id=order_id)

@login_required
def parse_address(request):
    """解析地址文本"""
    if request.method == 'POST':
        try:
            text = json.loads(request.body)['text']
            
            # 解析手机号
            phone_pattern = r'1[3-9]\d{9}'
            phone = re.findall(phone_pattern, text)
            
            # 解析邮编
            postcode_pattern = r'\d{6}'
            postcode = re.findall(postcode_pattern, text)
            
            # 解析省市区
            # 这里需要一个更复杂的地址解析算法
            # 暂时返回示例数据
            result = {
                'name': '',  # 需要实现姓名提取
                'phone': phone[0] if phone else '',
                'postcode': postcode[0] if postcode else '',
                'province': '',  # 需要实现省份提取
                'city': '',  # 需要实现城市提取
                'address': text  # 完整地址
            }
            
            return JsonResponse({'success': True, 'data': result})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
            
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def search_sku(request):
    """搜索SKU"""
    query = request.GET.get('q', '')
    if query:
        skus = SKU.objects.filter(sku_code__icontains=query)[:10]
        results = [{
            'id': sku.id,
            'sku_code': sku.sku_code,
            'sku_name': sku.sku_name,
            'image_url': sku.img_url
        } for sku in skus]
        return JsonResponse({'results': results})
    return JsonResponse({'results': []})

@login_required
def sync_orders(request):
    """同步订单数据"""
    if request.method == 'POST':
        try:
            from .sync import sync_all_trade
            success, message = sync_all_trade()
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
        except Exception as e:
            messages.error(request, f"同步失败: {str(e)}")
            
    return redirect('trade:order_list')
