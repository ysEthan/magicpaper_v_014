from django import forms
from .models import StockInRecord, StockInDetail, StockOutRecord, StockOutDetail

class StockInForm(forms.ModelForm):
    class Meta:
        model = StockInRecord
        fields = ['warehouse', 'source_type', 'source_no', 'operator', 'remark']
        widgets = {
            'warehouse': forms.Select(attrs={'class': 'form-select'}),
            'source_type': forms.Select(attrs={'class': 'form-select'}),
            'source_no': forms.TextInput(attrs={'class': 'form-control'}),
            'operator': forms.Select(attrs={'class': 'form-select'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class StockInDetailForm(forms.ModelForm):
    class Meta:
        model = StockInDetail
        fields = ['sku', 'quantity', 'cost', 'allocation', 'remark']
        widgets = {
            'sku': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'allocation': forms.Select(attrs={'class': 'form-select'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置SKU选择器的查询集
        self.fields['sku'].queryset = self.fields['sku'].queryset.order_by('sku_code')

class StockOutDetailForm(forms.ModelForm):
    class Meta:
        model = StockOutDetail
        fields = ['sku', 'quantity', 'cost', 'allocation', 'remark']
        widgets = {
            'sku': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'cost': forms.NumberInput(attrs={'class': 'form-control'}),
            'allocation': forms.Select(attrs={'class': 'form-select'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置SKU选择器的查询集
        self.fields['sku'].queryset = self.fields['sku'].queryset.order_by('sku_code') 