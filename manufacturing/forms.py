from django import forms
from .models import Factory, ProductionOrder, SampleReview

class FactoryForm(forms.ModelForm):
    class Meta:
        model = Factory
        fields = ['name', 'code', 'contact', 'phone', 'address', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'contact': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

class ProductionOrderForm(forms.ModelForm):
    class Meta:
        model = ProductionOrder
        fields = [
            'order_type', 'sku', 'quantity', 'factory',
            'unit_price', 'expected_date', 'delivery_date',
            'follower', 'remark'
        ]
        widgets = {
            'order_type': forms.Select(attrs={'class': 'form-select'}),
            'sku': forms.Select(attrs={'class': 'form-select'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'factory': forms.Select(attrs={'class': 'form-select'}),
            'unit_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'expected_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'delivery_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'follower': forms.Select(attrs={'class': 'form-select'}),
            'remark': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 设置SKU选择器的查询集
        self.fields['sku'].queryset = self.fields['sku'].queryset.order_by('sku_code')
        # 设置工厂选择器的查询集
        self.fields['factory'].queryset = Factory.objects.filter(is_active=True)

    def clean(self):
        cleaned_data = super().clean()
        expected_date = cleaned_data.get('expected_date')
        delivery_date = cleaned_data.get('delivery_date')

        if expected_date and delivery_date and expected_date > delivery_date:
            raise forms.ValidationError('预计完成日期不能晚于预计交货日期')

        return cleaned_data

class SampleReviewForm(forms.ModelForm):
    class Meta:
        model = SampleReview
        fields = ['review_date', 'content', 'conclusion', 'attachments']
        widgets = {
            'review_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'conclusion': forms.TextInput(attrs={'class': 'form-control'}),
            'attachments': forms.HiddenInput()
        }

    def clean_attachments(self):
        attachments = self.cleaned_data.get('attachments')
        if not isinstance(attachments, list):
            return []
        return attachments 