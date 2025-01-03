from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

# 尝试导入所需的模型，如果模型不存在则使用占位数据
try:
    from trade.models import Order
    TRADE_MODELS_EXIST = True
except ImportError:
    TRADE_MODELS_EXIST = False

try:
    from storage.models import Stock
    STORAGE_MODELS_EXIST = True
except ImportError:
    STORAGE_MODELS_EXIST = False

try:
    from procurement.models import PurchaseOrder
    PROCUREMENT_MODELS_EXIST = True
except ImportError:
    PROCUREMENT_MODELS_EXIST = False

try:
    from gallery.models import SKU
    GALLERY_MODELS_EXIST = True
except ImportError:
    GALLERY_MODELS_EXIST = False

try:
    from manufacturing.models import ProductionOrder
    MANUFACTURING_MODELS_EXIST = True
except ImportError:
    MANUFACTURING_MODELS_EXIST = False

@login_required
def home_view(request):
    """主页视图"""
    # 获取当前日期和时间
    now = timezone.now()
    today = now.date()
    this_month_start = today.replace(day=1)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # 订单统计
    order_stats = {
        'pending_count': 0,
        'processing_count': 0,
        'today_order_count': 0,
        'month_order_count': 0,
        'last_month_order_count': 0,
        'mom_rate': 0,  # 环比增长率
    }
    
    if TRADE_MODELS_EXIST:
        month_order_count = Order.objects.filter(created_at__date__gte=this_month_start).count()
        last_month_order_count = Order.objects.filter(
            created_at__date__gte=last_month_start,
            created_at__date__lt=this_month_start
        ).count()
        
        # 计算环比增长率
        if last_month_order_count > 0:
            mom_rate = (month_order_count - last_month_order_count) / last_month_order_count * 100
        else:
            mom_rate = 0
        
        order_stats.update({
            'pending_count': Order.objects.filter(status='pending').count(),
            'processing_count': Order.objects.filter(status='processing').count(),
            'today_order_count': Order.objects.filter(created_at__date=today).count(),
            'month_order_count': month_order_count,
            'last_month_order_count': last_month_order_count,
            'mom_rate': mom_rate,
        })
    
    # 采购统计
    purchase_stats = {
        'pending_count': 0,
        'pending_payment_count': 0,
        'pending_storage_count': 0,
    }
    
    if PROCUREMENT_MODELS_EXIST:
        purchase_stats.update({
            'pending_count': PurchaseOrder.objects.filter(status=PurchaseOrder.Status.PENDING_ORDER).count(),
            'pending_payment_count': PurchaseOrder.objects.filter(status=PurchaseOrder.Status.PENDING_PAYMENT).count(),
            'pending_storage_count': PurchaseOrder.objects.filter(status=PurchaseOrder.Status.PENDING_STORAGE).count(),
        })
    
    # 库存统计
    stock_stats = {
        'total_sku_count': 0,
        'out_of_stock_count': 0,
        'low_stock_count': 0,
    }
    
    if STORAGE_MODELS_EXIST and GALLERY_MODELS_EXIST:
        stock_stats.update({
            'total_sku_count': SKU.objects.count(),
            'out_of_stock_count': Stock.objects.filter(stock_num=0).count(),
            'low_stock_count': Stock.objects.filter(stock_num__gt=0, stock_num__lte=10).count(),
        })
    
    # 生产统计
    production_stats = {
        'pending_count': 0,
        'in_production_count': 0,
        'sample_review_count': 0,
        'today_production_count': 0,
    }
    
    if MANUFACTURING_MODELS_EXIST:
        production_stats.update({
            'pending_count': ProductionOrder.objects.filter(status=ProductionOrder.OrderStatus.PENDING).count(),
            'in_production_count': ProductionOrder.objects.filter(status=ProductionOrder.OrderStatus.IN_PRODUCTION).count(),
            'sample_review_count': ProductionOrder.objects.filter(
                order_type=ProductionOrder.OrderType.SAMPLE,
                status=ProductionOrder.OrderStatus.PENDING
            ).count(),
            'today_production_count': ProductionOrder.objects.filter(created_at__date=today).count(),
        })
    
    # 获取最近的订单
    recent_orders = []
    if TRADE_MODELS_EXIST:
        recent_orders = Order.objects.all().order_by('-created_at')[:5]
    
    # 获取最近的采购单
    recent_purchases = []
    if PROCUREMENT_MODELS_EXIST:
        recent_purchases = PurchaseOrder.objects.all().order_by('-created_at')[:5]
    
    # 获取最近的生产订单
    recent_productions = []
    if MANUFACTURING_MODELS_EXIST:
        recent_productions = ProductionOrder.objects.all().order_by('-created_at')[:5]
    
    context = {
        'order_stats': order_stats,
        'purchase_stats': purchase_stats,
        'stock_stats': stock_stats,
        'production_stats': production_stats,
        'recent_orders': recent_orders,
        'recent_purchases': recent_purchases,
        'recent_productions': recent_productions,
    }
    
    return render(request, 'page/home.html', context)
