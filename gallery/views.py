from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Brand, Category, SPU, SKU

@login_required
def brand_list(request):
    """品牌列表"""
    brands = Brand.objects.all()
    
    # 搜索
    search_query = request.GET.get('search', '')
    if search_query:
        brands = brands.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # 状态过滤
    status = request.GET.get('status')
    if status is not None:
        brands = brands.filter(status=status)
    
    # 分页
    paginator = Paginator(brands, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status': status,
    }
    return render(request, 'gallery/brand_list.html', context)

@login_required
def category_list(request):
    """类目列表视图"""
    # 获取查询参数
    search_query = request.GET.get('search', '')
    level = request.GET.get('level', '')
    status = request.GET.get('status', '')
    
    # 构建查询条件
    categories = Category.objects.all()
    if search_query:
        categories = categories.filter(
            Q(category_name_zh__icontains=search_query) |
            Q(category_name_en__icontains=search_query)
        )
    if level:
        categories = categories.filter(level=level)
    if status:
        categories = categories.filter(status=status == '1')
    
    # 排序
    categories = categories.order_by('rank_id', '-created_at')
    
    # 分页
    paginator = Paginator(categories, 10)  # 每页显示10条
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 获取所有可用作父类目的类目
    all_categories = Category.objects.filter(status=True).exclude(is_last_level=True)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'level': level,
        'status': status,
        'categories': all_categories,
        'category': Category,  # 用于模板中访问 LEVEL_CHOICES
    }
    return render(request, 'gallery/category_list.html', context)

@login_required
def category_create(request):
    """创建类目"""
    if request.method == 'POST':
        category_name_zh = request.POST.get('category_name_zh')
        category_name_en = request.POST.get('category_name_en')
        level = request.POST.get('level')
        parent_id = request.POST.get('parent')
        description = request.POST.get('description')
        rank_id = request.POST.get('rank_id', 0)
        is_last_level = request.POST.get('is_last_level') == 'on'
        status = request.POST.get('status') == '1'
        
        try:
            category = Category.objects.create(
                category_name_zh=category_name_zh,
                category_name_en=category_name_en,
                level=level,
                parent_id=parent_id or None,
                description=description,
                rank_id=rank_id,
                is_last_level=is_last_level,
                status=status
            )
            
            # 处理图片上传
            if 'image' in request.FILES:
                category.image = request.FILES['image']
                category.save()
            
            messages.success(request, f'类目 "{category_name_zh}" 创建成功！')
        except Exception as e:
            messages.error(request, f'创建类目失败：{str(e)}')
        
    return redirect('gallery:category_list')

@login_required
def category_edit(request, pk):
    """编辑类目"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        category.category_name_zh = request.POST.get('category_name_zh')
        category.category_name_en = request.POST.get('category_name_en')
        category.level = request.POST.get('level')
        parent_id = request.POST.get('parent')
        category.parent_id = parent_id or None
        category.description = request.POST.get('description')
        category.rank_id = request.POST.get('rank_id', 0)
        category.is_last_level = request.POST.get('is_last_level') == 'on'
        category.status = request.POST.get('status') == '1'
        
        try:
            # 处理图片上传
            if 'image' in request.FILES:
                category.image = request.FILES['image']
            
            category.save()
            messages.success(request, f'类目 "{category.category_name_zh}" 更新成功！')
        except Exception as e:
            messages.error(request, f'更新类目失败：{str(e)}')
        
    return redirect('gallery:category_list')

@login_required
def category_delete(request, pk):
    """删除类目"""
    category = get_object_or_404(Category, pk=pk)
    
    if request.method == 'POST':
        try:
            category_name = category.category_name_zh
            # 检查是否有子类目
            if category.children.exists():
                messages.error(request, f'无法删除类目 "{category_name}"：该类目下存在子类目')
            else:
                category.delete()
                messages.success(request, f'类目 "{category_name}" 已删除')
        except Exception as e:
            messages.error(request, f'删除类目失败：{str(e)}')
    
    return redirect('gallery:category_list')

@login_required
def spu_list(request):
    """SPU列表"""
    spus = SPU.objects.all()
    
    # 搜索
    search_query = request.GET.get('search', '')
    if search_query:
        spus = spus.filter(
            Q(spu_code__icontains=search_query) |
            Q(spu_name__icontains=search_query)
        )
    
    # 产品类型过滤
    product_type = request.GET.get('product_type')
    if product_type:
        spus = spus.filter(product_type=product_type)
    
    # 品牌过滤
    brand_id = request.GET.get('brand')
    if brand_id:
        spus = spus.filter(brand_id=brand_id)
    
    # 类目过滤
    category_id = request.GET.get('category')
    if category_id:
        spus = spus.filter(category_id=category_id)
    
    # 状态过滤
    status = request.GET.get('status')
    if status:
        spus = spus.filter(status=status == '1')
    
    # 排序
    spus = spus.order_by('-created_at')
    
    # 分页
    paginator = Paginator(spus, 10)  # 每页显示10条
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 获取所有品牌和类目，用于过滤选项
    brands = Brand.objects.filter(status=True)
    categories = Category.objects.filter(status=True, is_last_level=True)
    
    # 获取所有用户，用于选择专员
    from django.contrib.auth.models import User
    users = User.objects.filter(is_active=True)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'product_type': product_type,
        'brand_id': brand_id,
        'category_id': category_id,
        'status': status,
        'brands': brands,
        'categories': categories,
        'users': users,
        'SPU': SPU,  # 用于模板中访问 PRODUCT_TYPE_CHOICES
    }
    return render(request, 'gallery/spu_list.html', context)

@login_required
def sku_list(request):
    """SKU列表"""
    skus = SKU.objects.all()
    
    # 搜索
    search_query = request.GET.get('search', '')
    if search_query:
        skus = skus.filter(
            Q(sku_code__icontains=search_query) |
            Q(sku_name__icontains=search_query) |
            Q(material__icontains=search_query) |
            Q(color__icontains=search_query)
        )
    
    # SPU过滤
    spu_id = request.GET.get('spu')
    if spu_id:
        skus = skus.filter(spu_id=spu_id)
    
    # 电镀工艺过滤
    plating_process = request.GET.get('plating_process')
    if plating_process:
        skus = skus.filter(plating_process=plating_process)
    
    # 表面处理过滤
    surface_treatment = request.GET.get('surface_treatment')
    if surface_treatment:
        skus = skus.filter(surface_treatment=surface_treatment)
    
    # 状态过滤
    status = request.GET.get('status')
    if status:
        skus = skus.filter(status=status == '1')
    
    # 排序
    skus = skus.order_by('-created_at')
    
    # 分页
    paginator = Paginator(skus, 10)  # 每页显示10条
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # 获取所有SPU，用于过滤和创建/编辑SKU
    spus = SPU.objects.filter(status=True)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'spu_id': spu_id,
        'plating_process': plating_process,
        'surface_treatment': surface_treatment,
        'status': status,
        'spus': spus,
        'PLATING_PROCESS_CHOICES': SKU.PLATING_PROCESS_CHOICES,
        'SURFACE_TREATMENT_CHOICES': SKU.SURFACE_TREATMENT_CHOICES,
    }
    return render(request, 'gallery/sku_list.html', context)

@login_required
def sku_detail(request, sku_code):
    """SKU详情"""
    sku = get_object_or_404(SKU, sku_code=sku_code)
    return render(request, 'gallery/sku_detail.html', {'sku': sku})

@login_required
def spu_create(request):
    """创建SPU"""
    if request.method == 'POST':
        spu_code = request.POST.get('spu_code')
        spu_name = request.POST.get('spu_name')
        product_type = request.POST.get('product_type')
        brand_id = request.POST.get('brand')
        category_id = request.POST.get('category')
        poc_id = request.POST.get('poc')
        sales_channel = request.POST.get('sales_channel')
        spu_remark = request.POST.get('spu_remark')
        status = request.POST.get('status') == '1'
        
        try:
            spu = SPU.objects.create(
                spu_code=spu_code,
                spu_name=spu_name,
                product_type=product_type,
                brand_id=brand_id or None,
                category_id=category_id,
                poc_id=poc_id or None,
                sales_channel=sales_channel,
                spu_remark=spu_remark,
                status=status
            )
            messages.success(request, f'SPU "{spu_name}" 创建成功！')
        except Exception as e:
            messages.error(request, f'创建SPU失败：{str(e)}')
        
    return redirect('gallery:spu_list')

@login_required
def spu_edit(request, pk):
    """编辑SPU"""
    spu = get_object_or_404(SPU, pk=pk)
    
    if request.method == 'POST':
        spu.spu_code = request.POST.get('spu_code')
        spu.spu_name = request.POST.get('spu_name')
        spu.product_type = request.POST.get('product_type')
        brand_id = request.POST.get('brand')
        spu.brand_id = brand_id or None
        spu.category_id = request.POST.get('category')
        poc_id = request.POST.get('poc')
        spu.poc_id = poc_id or None
        spu.sales_channel = request.POST.get('sales_channel')
        spu.spu_remark = request.POST.get('spu_remark')
        spu.status = request.POST.get('status') == '1'
        
        try:
            spu.save()
            messages.success(request, f'SPU "{spu.spu_name}" 更新成功！')
        except Exception as e:
            messages.error(request, f'更新SPU失败：{str(e)}')
        
    return redirect('gallery:spu_list')

@login_required
def spu_delete(request, pk):
    """删除SPU"""
    spu = get_object_or_404(SPU, pk=pk)
    
    if request.method == 'POST':
        try:
            spu_name = spu.spu_name
            # 检查是否有关联的SKU
            if spu.sku_set.exists():
                messages.error(request, f'无法删除SPU "{spu_name}"：该SPU下存在SKU')
            else:
                spu.delete()
                messages.success(request, f'SPU "{spu_name}" 已删除')
        except Exception as e:
            messages.error(request, f'删除SPU失败：{str(e)}')
    
    return redirect('gallery:spu_list')

@login_required
def sku_create(request):
    """创建SKU"""
    if request.method == 'POST':
        sku_code = request.POST.get('sku_code')
        sku_name = request.POST.get('sku_name')
        spu_id = request.POST.get('spu')
        material = request.POST.get('material')
        color = request.POST.get('color')
        plating_process = request.POST.get('plating_process')
        surface_treatment = request.POST.get('surface_treatment')
        weight = request.POST.get('weight')
        size = request.POST.get('size')
        sku_remark = request.POST.get('sku_remark')
        status = request.POST.get('status') == '1'
        
        try:
            sku = SKU.objects.create(
                sku_code=sku_code,
                sku_name=sku_name,
                spu_id=spu_id,
                material=material,
                color=color,
                plating_process=plating_process,
                surface_treatment=surface_treatment,
                weight=weight or None,
                size=size,
                sku_remark=sku_remark,
                status=status
            )
            messages.success(request, f'SKU "{sku_name}" 创建成功！')
        except Exception as e:
            messages.error(request, f'创建SKU失败：{str(e)}')
        
    return redirect('gallery:sku_list')

@login_required
def sku_edit(request, pk):
    """编辑SKU"""
    sku = get_object_or_404(SKU, pk=pk)
    
    if request.method == 'POST':
        sku.sku_code = request.POST.get('sku_code')
        sku.sku_name = request.POST.get('sku_name')
        sku.spu_id = request.POST.get('spu')
        sku.material = request.POST.get('material')
        sku.color = request.POST.get('color')
        sku.plating_process = request.POST.get('plating_process')
        sku.surface_treatment = request.POST.get('surface_treatment')
        weight = request.POST.get('weight')
        sku.weight = weight or None
        sku.size = request.POST.get('size')
        sku.sku_remark = request.POST.get('sku_remark')
        sku.status = request.POST.get('status') == '1'
        
        try:
            sku.save()
            messages.success(request, f'SKU "{sku.sku_name}" 更新成功！')
        except Exception as e:
            messages.error(request, f'更新SKU失败：{str(e)}')
        
    return redirect('gallery:sku_list')

@login_required
def sku_delete(request, pk):
    """删除SKU"""
    sku = get_object_or_404(SKU, pk=pk)
    
    if request.method == 'POST':
        try:
            sku_name = sku.sku_name
            # 检查是否有关联的库存记录
            if sku.stock_set.exists():
                messages.error(request, f'无法删除SKU "{sku_name}"：该SKU存在库存记录')
            else:
                sku.delete()
                messages.success(request, f'SKU "{sku_name}" 已删除')
        except Exception as e:
            messages.error(request, f'删除SKU失败：{str(e)}')
    
    return redirect('gallery:sku_list')
