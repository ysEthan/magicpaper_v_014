from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import (
    Warehouse, Allocation, Stock, StockInRecord, StockInDetail,
    StockOutRecord, StockOutDetail
)
from .forms import StockInForm, StockInDetailForm, StockOutDetailForm

class WarehouseListView(LoginRequiredMixin, ListView):
    model = Warehouse
    template_name = 'storage/warehouse_list.html'
    context_object_name = 'warehouses'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Warehouse.objects.filter(
                Q(name__icontains=query) |
                Q(address__icontains=query) |
                Q(contact__icontains=query) |
                Q(contact_phone__icontains=query)
            ).order_by('-created_at')
        return Warehouse.objects.all().order_by('-created_at')

class WarehouseCreateView(LoginRequiredMixin, CreateView):
    model = Warehouse
    template_name = 'storage/warehouse_form.html'
    fields = ['name', 'address', 'contact', 'contact_phone']
    success_url = reverse_lazy('storage:warehouse-list')

    def form_valid(self, form):
        messages.success(self.request, '仓库创建成功！')
        return super().form_valid(form)

class WarehouseUpdateView(LoginRequiredMixin, UpdateView):
    model = Warehouse
    template_name = 'storage/warehouse_form.html'
    fields = ['name', 'address', 'contact', 'contact_phone']
    success_url = reverse_lazy('storage:warehouse-list')

    def form_valid(self, form):
        messages.success(self.request, '仓库更新成功！')
        return super().form_valid(form)

class WarehouseDeleteView(LoginRequiredMixin, DeleteView):
    model = Warehouse
    template_name = 'storage/warehouse_confirm_delete.html'
    success_url = reverse_lazy('storage:warehouse-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, '仓库删除成功！')
        return super().delete(request, *args, **kwargs)

class AllocationListView(LoginRequiredMixin, ListView):
    model = Allocation
    template_name = 'storage/allocation_list.html'
    context_object_name = 'allocations'
    paginate_by = 10

    def get_queryset(self):
        warehouse_id = self.request.GET.get('warehouse')
        query = self.request.GET.get('q')
        
        queryset = Allocation.objects.all()
        
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
            
        if query:
            queryset = queryset.filter(
                Q(area_code__icontains=query) |
                Q(area_name__icontains=query) |
                Q(location_code__icontains=query)
            )
            
        return queryset.order_by('warehouse', 'area_code', 'location_code')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouses'] = Warehouse.objects.all()
        context['current_warehouse'] = self.request.GET.get('warehouse', '')
        return context

class AllocationCreateView(LoginRequiredMixin, CreateView):
    model = Allocation
    template_name = 'storage/allocation_form.html'
    fields = ['warehouse', 'area_code', 'area_name', 'area_type', 'location_code']
    success_url = reverse_lazy('storage:allocation-list')

    def form_valid(self, form):
        messages.success(self.request, '货位创建成功！')
        return super().form_valid(form)

class AllocationUpdateView(LoginRequiredMixin, UpdateView):
    model = Allocation
    template_name = 'storage/allocation_form.html'
    fields = ['warehouse', 'area_code', 'area_name', 'area_type', 'location_code']
    success_url = reverse_lazy('storage:allocation-list')

    def form_valid(self, form):
        messages.success(self.request, '货位更新成功！')
        return super().form_valid(form)

class AllocationDeleteView(LoginRequiredMixin, DeleteView):
    model = Allocation
    template_name = 'storage/allocation_confirm_delete.html'
    success_url = reverse_lazy('storage:allocation-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, '货位删除成功！')
        return super().delete(request, *args, **kwargs)

class StockListView(LoginRequiredMixin, ListView):
    model = Stock
    template_name = 'storage/stock_list.html'
    context_object_name = 'stocks'
    paginate_by = 10

    def get_queryset(self):
        warehouse_id = self.request.GET.get('warehouse')
        query = self.request.GET.get('q')
        
        queryset = Stock.objects.all()
        
        if warehouse_id:
            queryset = queryset.filter(warehouse_id=warehouse_id)
            
        if query:
            queryset = queryset.filter(
                Q(sku__sku_code__icontains=query) |
                Q(sku__sku_name__icontains=query)
            )
            
        return queryset.select_related('sku', 'warehouse').order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouses'] = Warehouse.objects.all()
        context['current_warehouse'] = self.request.GET.get('warehouse', '')
        return context

class StockInRecordListView(LoginRequiredMixin, ListView):
    model = StockInRecord
    context_object_name = 'stock_ins'
    template_name = 'storage/stock_in_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        warehouse = self.request.GET.get('warehouse')
        q = self.request.GET.get('q')
        
        if warehouse:
            queryset = queryset.filter(warehouse_id=warehouse)
        if q:
            queryset = queryset.filter(
                Q(stock_in_no__icontains=q) |
                Q(source_no__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouses'] = Warehouse.objects.all()
        context['current_warehouse'] = self.request.GET.get('warehouse', '')
        return context

class StockInRecordCreateView(LoginRequiredMixin, CreateView):
    model = StockInRecord
    fields = ['warehouse', 'source_type', 'source_no', 'operator', 'remark']
    template_name = 'storage/stock_in_form.html'
    success_url = reverse_lazy('storage:stock-in-list')

    def form_valid(self, form):
        messages.success(self.request, '入库单创建成功')
        return super().form_valid(form)

class StockInRecordDetailView(LoginRequiredMixin, DetailView):
    model = StockInRecord
    context_object_name = 'stock_in'
    template_name = 'storage/stock_in_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = self.object.details.all()
        return context

class StockOutRecordListView(LoginRequiredMixin, ListView):
    model = StockOutRecord
    context_object_name = 'stock_outs'
    template_name = 'storage/stock_out_list.html'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset()
        warehouse = self.request.GET.get('warehouse')
        q = self.request.GET.get('q')
        
        if warehouse:
            queryset = queryset.filter(warehouse_id=warehouse)
        if q:
            queryset = queryset.filter(
                Q(stock_out_no__icontains=q) |
                Q(source_no__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['warehouses'] = Warehouse.objects.all()
        context['current_warehouse'] = self.request.GET.get('warehouse', '')
        return context

class StockOutRecordCreateView(LoginRequiredMixin, CreateView):
    model = StockOutRecord
    fields = ['warehouse', 'source_type', 'source_no', 'operator', 'remark']
    template_name = 'storage/stock_out_form.html'
    success_url = reverse_lazy('storage:stock-out-list')

    def form_valid(self, form):
        messages.success(self.request, '出库单创建成功')
        return super().form_valid(form)

class StockOutRecordDetailView(LoginRequiredMixin, DetailView):
    model = StockOutRecord
    context_object_name = 'stock_out'
    template_name = 'storage/stock_out_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['details'] = self.object.details.all()
        return context

@login_required
def stock_in_add_detail(request, pk):
    """添加入库单明细"""
    stock_in = get_object_or_404(StockInRecord, pk=pk)
    
    if request.method == 'POST':
        form = StockInDetailForm(request.POST)
        if form.is_valid():
            detail = form.save(commit=False)
            detail.stock_in = stock_in
            detail.save()
            
            # 更新库存
            stock, created = Stock.objects.get_or_create(
                sku=detail.sku,
                warehouse=stock_in.warehouse,
                defaults={'stock_num': 0}
            )
            stock.stock_num += detail.quantity
            stock.save()
            
            messages.success(request, '入库明细添加成功')
            return redirect('storage:stock-in-detail', pk=pk)
    else:
        form = StockInDetailForm()
    
    context = {
        'stock_in': stock_in,
        'form': form
    }
    return render(request, 'storage/stock_in_detail_form.html', context)

@login_required
def stock_in_delete_detail(request, pk, detail_pk):
    """删除入库单明细"""
    stock_in = get_object_or_404(StockInRecord, pk=pk)
    detail = get_object_or_404(StockInDetail, pk=detail_pk, stock_in=stock_in)
    
    # 如果入库单已经确认，不允许删除明细
    if stock_in.status != 'draft':
        messages.error(request, '只能删除草稿状态的入库单明细')
        return redirect('storage:stock-in-detail', pk=pk)
    
    # 删除明细
    detail.delete()
    messages.success(request, '入库明细删除成功')
    
    return redirect('storage:stock-in-detail', pk=pk)

@login_required
def stock_out_add_detail(request, pk):
    """添加出库单明细"""
    stock_out = get_object_or_404(StockOutRecord, pk=pk)
    
    if request.method == 'POST':
        form = StockOutDetailForm(request.POST)
        if form.is_valid():
            detail = form.save(commit=False)
            detail.stock_out = stock_out
            
            # 检查库存是否足够
            stock = Stock.objects.filter(
                warehouse=stock_out.warehouse,
                sku=detail.sku
            ).first()
            
            if not stock or stock.stock_num < detail.quantity:
                messages.error(request, '库存不足')
                return redirect('storage:stock-out-detail', pk=pk)
            
            detail.save()
            
            # 更新库存
            stock.stock_num -= detail.quantity
            stock.save()
            
            messages.success(request, '出库明细添加成功')
            return redirect('storage:stock-out-detail', pk=pk)
    else:
        form = StockOutDetailForm()
    
    context = {
        'stock_out': stock_out,
        'form': form
    }
    return render(request, 'storage/stock_out_detail_form.html', context)

@login_required
def stock_out_delete_detail(request, pk, detail_pk):
    """删除出库单明细"""
    stock_out = get_object_or_404(StockOutRecord, pk=pk)
    detail = get_object_or_404(StockOutDetail, pk=detail_pk, stock_out=stock_out)
    
    # 如果出库单已经确认，不允许删除明细
    if stock_out.status != 'draft':
        messages.error(request, '只能删除草稿状态的出库单明细')
        return redirect('storage:stock-out-detail', pk=pk)
    
    # 恢复库存
    stock = Stock.objects.filter(
        warehouse=stock_out.warehouse,
        sku=detail.sku
    ).first()
    
    if stock:
        stock.stock_num += detail.quantity
        stock.save()
    
    # 删除明细
    detail.delete()
    messages.success(request, '出库明细删除成功')
    
    return redirect('storage:stock-out-detail', pk=pk)
