from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import time
import hashlib
import json
import math
import requests
from datetime import datetime, timedelta
from .models import Supplier, PurchaseOrder, PurchaseOrderDetail

class SupplierListView(LoginRequiredMixin, ListView):
    model = Supplier
    template_name = 'procurement/supplier_list.html'
    context_object_name = 'suppliers'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Supplier.objects.filter(
                Q(name__icontains=query) |
                Q(contact_info__icontains=query)
            ).order_by('-created_at')
        return Supplier.objects.all().order_by('-created_at')

class SupplierCreateView(LoginRequiredMixin, CreateView):
    model = Supplier
    template_name = 'procurement/supplier_form.html'
    fields = ['name', 'contact_info']
    success_url = reverse_lazy('supplier-list')

    def form_valid(self, form):
        messages.success(self.request, '供应商创建成功！')
        return super().form_valid(form)

class SupplierUpdateView(LoginRequiredMixin, UpdateView):
    model = Supplier
    template_name = 'procurement/supplier_form.html'
    fields = ['name', 'contact_info']
    success_url = reverse_lazy('supplier-list')

    def form_valid(self, form):
        messages.success(self.request, '供应商更新成功！')
        return super().form_valid(form)

class SupplierDeleteView(LoginRequiredMixin, DeleteView):
    model = Supplier
    template_name = 'procurement/supplier_confirm_delete.html'
    success_url = reverse_lazy('supplier-list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, '供应商删除成功！')
        return super().delete(request, *args, **kwargs)

class PurchaseOrderListView(LoginRequiredMixin, ListView):
    model = PurchaseOrder
    template_name = 'procurement/purchase_order_list.html'
    context_object_name = 'purchase_orders'
    paginate_by = 10

    def get_queryset(self):
        status = self.request.GET.get('status')
        query = self.request.GET.get('q')
        
        queryset = PurchaseOrder.objects.all()
        
        if status and status.isdigit():
            queryset = queryset.filter(status=int(status))
            
        if query:
            queryset = queryset.filter(
                Q(purchase_order_number__icontains=query) |
                Q(supplier__name__icontains=query)
            )
            
        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_choices'] = PurchaseOrder.STATUS_CHOICES
        context['current_status'] = self.request.GET.get('status', '')
        return context

class PurchaseOrderCreateView(LoginRequiredMixin, CreateView):
    model = PurchaseOrder
    template_name = 'procurement/purchase_order_form.html'
    fields = ['purchase_order_number', 'supplier', 'warehouse', 'purchase_date', 
             'expected_delivery_date', 'status']
    success_url = reverse_lazy('purchase-order-list')

    def form_valid(self, form):
        messages.success(self.request, '采购单创建成功！')
        return super().form_valid(form)

class PurchaseOrderUpdateView(LoginRequiredMixin, UpdateView):
    model = PurchaseOrder
    template_name = 'procurement/purchase_order_form.html'
    fields = ['supplier', 'warehouse', 'purchase_date', 'expected_delivery_date', 'status']
    success_url = reverse_lazy('purchase-order-list')

    def form_valid(self, form):
        messages.success(self.request, '采购单更新成功！')
        return super().form_valid(form)

class PurchaseOrderDetailView(LoginRequiredMixin, ListView):
    model = PurchaseOrderDetail
    template_name = 'procurement/purchase_order_detail.html'
    context_object_name = 'details'
    paginate_by = 10

    def get_queryset(self):
        self.purchase_order = get_object_or_404(PurchaseOrder, pk=self.kwargs['pk'])
        return PurchaseOrderDetail.objects.filter(purchase_order=self.purchase_order)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['purchase_order'] = self.purchase_order
        return context

@login_required
@require_POST
def sync_purchase_orders(request):
    """同步采购单数据"""
    try:
        # 设置同步的时间范围（最近7天的订单）
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        
        # API配置
        app_name = "mathmagic"
        app_key = "82be0592545283da00744b489f758f99"
        sid = "mathmagic"
        
        # 准备请求数据
        body = {
            "pageSize": 100,
            "pageNo": 1,
            "createTimeBegin": start_date,
            "createTimeEnd": end_date,
            "orderStatus": [40, 42, 75, 70, 10],  # 待下单 待支付 待入库 已完成 已作废
            "account": "admin"
        }
        
        body_str = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
        
        # 生成签名
        timestamp = str(int(time.time()))
        sign_str = f"{app_key}appName{app_name}body{body_str}sid{sid}timestamp{timestamp}{app_key}"
        sign = hashlib.md5(sign_str.encode()).hexdigest()
        
        params = {
            "appName": app_name,
            "sid": sid,
            "sign": sign,
            "timestamp": timestamp,
        }
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        # 发送API请求
        url = "https://openapi.qizhishangke.com/api/openservices/purchaseOrder/v1/getOrders"
        response = requests.post(url, params=params, headers=headers, data=body_str.encode('utf-8'))
        
        if response.status_code != 200:
            return JsonResponse({
                'success': False,
                'message': f"API请求失败: {response.text}"
            })
            
        result = response.json()
        if result['code'] != 200:
            return JsonResponse({
                'success': False,
                'message': f"业务处理失败: {result['message']}"
            })
            
        # 处理返回的数据
        data = result['data']
        success_count = 0
        error_count = 0
        
        for item in data['data']:
            try:
                # 获取或创建供应商
                supplier, _ = Supplier.objects.get_or_create(
                    name=item['providerName'],
                    defaults={
                        'contact_info': item.get('providerNo', '')
                    }
                )
                
                # 创建或更新采购单
                purchase_order_data = {
                    'supplier': supplier,
                    'purchase_date': datetime.strptime(item['created'], "%Y-%m-%d %H:%M:%S").date(),
                    'expected_delivery_date': datetime.strptime(item['tradeTime'], "%Y-%m-%d %H:%M:%S").date(),
                    'status': item['orderStatus'],
                    'total_amount': float(item.get('payment', 0))
                }
                
                purchase_order, created = PurchaseOrder.objects.update_or_create(
                    purchase_order_number=item['purchaseNo'],
                    defaults=purchase_order_data
                )
                
                # 处理采购单明细
                for detail in item['purchaseOrderDetailsVOList']:
                    try:
                        from gallery.models import SKU
                        sku = SKU.objects.get(sku_code=detail['specNo'])
                        
                        detail_data = {
                            'purchase_order': purchase_order,
                            'product': sku,
                            'quantity': float(detail['num']),
                            'unit_price': float(detail.get('price', 0)),
                            'amount': float(detail['num']) * float(detail.get('price', 0))
                        }
                        
                        PurchaseOrderDetail.objects.update_or_create(
                            purchase_order=purchase_order,
                            product=sku,
                            defaults=detail_data
                        )
                        
                    except SKU.DoesNotExist:
                        print(f"SKU不存在: {detail['specNo']}")
                        continue
                    except Exception as e:
                        print(f"处理采购单明细失败: {str(e)}")
                        continue
                        
                success_count += 1
                
            except Exception as e:
                print(f"处理采购单失败: {str(e)}")
                error_count += 1
                continue
        
        return JsonResponse({
            'success': True,
            'message': f"同步完成，成功: {success_count} 条，失败: {error_count} 条"
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f"同步失败: {str(e)}"
        })
