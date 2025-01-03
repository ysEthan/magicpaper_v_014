from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from .models import Factory, ProductionOrder, SampleReview
from .forms import FactoryForm, ProductionOrderForm, SampleReviewForm

@login_required
def factory_list(request):
    """工厂列表"""
    factories = Factory.objects.all()
    
    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        factories = factories.filter(
            Q(name__icontains=search_query) |
            Q(code__icontains=search_query)
        )
    
    # 分页
    paginator = Paginator(factories, 10)
    page = request.GET.get('page')
    factories = paginator.get_page(page)
    
    context = {
        'factories': factories,
        'search_query': search_query
    }
    return render(request, 'manufacturing/factory_list.html', context)

@login_required
def factory_create(request):
    """创建工厂"""
    if request.method == 'POST':
        form = FactoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '工厂创建成功')
            return redirect('factory_list')
    else:
        form = FactoryForm()
    
    return render(request, 'manufacturing/factory_form.html', {'form': form})

@login_required
def factory_edit(request, pk):
    """编辑工厂"""
    factory = get_object_or_404(Factory, pk=pk)
    if request.method == 'POST':
        form = FactoryForm(request.POST, instance=factory)
        if form.is_valid():
            form.save()
            messages.success(request, '工厂信息更新成功')
            return redirect('factory_list')
    else:
        form = FactoryForm(instance=factory)
    
    return render(request, 'manufacturing/factory_form.html', {'form': form})

@login_required
def production_order_list(request):
    """生产订单列表"""
    orders = ProductionOrder.objects.all()
    
    # 状态筛选
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    
    # 订单类型筛选
    order_type = request.GET.get('type')
    if order_type:
        orders = orders.filter(order_type=order_type)
    
    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        orders = orders.filter(
            Q(order_no__icontains=search_query) |
            Q(sku__sku_code__icontains=search_query) |
            Q(factory__name__icontains=search_query)
        )
    
    # 分页
    paginator = Paginator(orders, 10)
    page = request.GET.get('page')
    orders = paginator.get_page(page)
    
    context = {
        'orders': orders,
        'status': status,
        'order_type': order_type,
        'search_query': search_query
    }
    return render(request, 'manufacturing/production_order_list.html', context)

@login_required
def production_order_create(request):
    """创建生产订单"""
    if request.method == 'POST':
        form = ProductionOrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.creator = request.user
            order.save()
            messages.success(request, '生产订单创建成功')
            return redirect('production_order_list')
    else:
        form = ProductionOrderForm()
    
    return render(request, 'manufacturing/production_order_form.html', {'form': form})

@login_required
def production_order_edit(request, pk):
    """编辑生产订单"""
    order = get_object_or_404(ProductionOrder, pk=pk)
    if request.method == 'POST':
        form = ProductionOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, '生产订单更新成功')
            return redirect('production_order_list')
    else:
        form = ProductionOrderForm(instance=order)
    
    return render(request, 'manufacturing/production_order_form.html', {'form': form})

@login_required
def sample_review_list(request, order_id):
    """样品评审列表"""
    order = get_object_or_404(ProductionOrder, pk=order_id)
    reviews = order.samplereview_set.all().order_by('-review_date')
    
    context = {
        'order': order,
        'reviews': reviews
    }
    return render(request, 'manufacturing/sample_review_list.html', context)

@login_required
def sample_review_create(request, order_id):
    """创建样品评审"""
    order = get_object_or_404(ProductionOrder, pk=order_id)
    if request.method == 'POST':
        form = SampleReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.production_order = order
            review.reviewer = request.user
            review.save()
            messages.success(request, '样品评审记录创建成功')
            return redirect('sample_review_list', order_id=order_id)
    else:
        form = SampleReviewForm()
    
    context = {
        'order': order,
        'form': form
    }
    return render(request, 'manufacturing/sample_review_form.html', context)
