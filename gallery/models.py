from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings
import os
from django.utils.translation import gettext_lazy as _

def category_image_path(instance, filename):
    """生成类目图片的存储路径"""
    ext = filename.split('.')[-1]
    new_filename = f"category_{instance.id}_{instance.category_name_en}.{ext}"
    return os.path.join('categories', new_filename)

class Brand(models.Model):
    """品牌"""
    name = models.CharField(max_length=100, verbose_name='品牌名称')
    description = models.TextField(blank=True, null=True, verbose_name='品牌描述')
    logo_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='logoURL')
    status = models.BooleanField(default=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'gallery_brand'
        verbose_name = '品牌'
        verbose_name_plural = '品牌列表'
        ordering = ['name']

    def __str__(self):
        return self.name

class Category(models.Model):
    """商品类目模型"""
    LEVEL_CHOICES = (
        (1, '一级类目'),
        (2, '二级类目'),
        (3, '三级类目'),
    )
    
    category_name_zh = models.CharField(_('中文名称'), max_length=50)
    category_name_en = models.CharField(_('英文名称'), max_length=50)
    level = models.IntegerField(_('层级'), choices=LEVEL_CHOICES)
    parent = models.ForeignKey('self', verbose_name=_('父类目'), null=True, blank=True,
                              on_delete=models.CASCADE, related_name='children')
    description = models.TextField(_('描述'), blank=True)
    image = models.ImageField(_('类目图片'), upload_to='categories/', null=True, blank=True)
    rank_id = models.IntegerField(_('排序ID'), default=0)
    is_last_level = models.BooleanField(_('是否最后一级'), default=False)
    status = models.BooleanField(_('状态'), default=True)
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    
    class Meta:
        verbose_name = _('商品类目')
        verbose_name_plural = _('商品类目')
        ordering = ['rank_id', '-created_at']
    
    def __str__(self):
        return self.category_name_zh
    
    def get_full_name(self):
        """获取完整的类目路径名称"""
        if self.parent:
            return f'{self.parent.get_full_name()} > {self.category_name_zh}'
        return self.category_name_zh

class SPU(models.Model):
    """SPU（标准产品单位）"""
    PRODUCT_TYPE_CHOICES = [
        ('math_design', '设计款'),
        ('ready_made', '现货款'),
        ('raw_material', '材料'),
        ('packing_material', '包材'),
    ]

    spu_code = models.CharField(max_length=50, unique=True, verbose_name='SPU编码')
    spu_name = models.CharField(max_length=100, verbose_name='SPU名称')
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, verbose_name='产品类型')
    spu_remark = models.TextField(blank=True, null=True, verbose_name='备注')
    sales_channel = models.CharField(max_length=20, blank=True, null=True, verbose_name='销售渠道')
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='品牌')
    poc = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='专员')
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT,
        verbose_name='类目',
        null=False,
        blank=False
    )
    status = models.BooleanField(default=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'gallery_spu'
        verbose_name = 'SPU'
        verbose_name_plural = 'SPU列表'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.spu_code} - {self.spu_name}"

class SKU(models.Model):
    """SKU（库存量单位）"""
    PLATING_PROCESS_CHOICES = (
        ('none', '无电镀'),
        ('gold', '镀金'),
        ('silver', '镀银'),
        ('nickel', '镀镍'),
        ('chrome', '镀铬'),
        ('copper', '镀铜'),
        ('other', '其他'),
    )
    
    SURFACE_TREATMENT_CHOICES = (
        ('none', '无处理'),
        ('antique', '做旧'),
        ('epoxy', '滴胶'),
        ('frosted', '磨砂'),
    )
    
    sku_code = models.CharField(max_length=50, unique=True, verbose_name='SKU编码')
    sku_name = models.CharField(max_length=100, verbose_name='SKU名称')
    spu = models.ForeignKey(SPU, on_delete=models.CASCADE, verbose_name='所属SPU', null=True)
    material = models.CharField(max_length=50, verbose_name='材质')
    color = models.CharField(max_length=50, verbose_name='颜色')
    plating_process = models.CharField(
        max_length=20, 
        choices=PLATING_PROCESS_CHOICES, 
        default='none',
        verbose_name='电镀工艺'
    )
    surface_treatment = models.CharField(
        max_length=20, 
        choices=SURFACE_TREATMENT_CHOICES,
        default='none',
        verbose_name='表面处理'
    )
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name='重量(g)')
    length = models.IntegerField(default=0, verbose_name='长度(mm)')
    width = models.IntegerField(default=0, verbose_name='宽度(mm)')
    height = models.IntegerField(default=0, verbose_name='高度(mm)')
    other_dimensions = models.CharField(max_length=25, null=True, blank=True, verbose_name='其他尺寸')
    suppliers_list = models.JSONField(verbose_name='供应商列表', default=list, blank=True)
    img_url = models.CharField(max_length=255, null=True, blank=True, verbose_name='图片URL')
    status = models.BooleanField(default=True, verbose_name='状态')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'gallery_sku'
        verbose_name = 'SKU'
        verbose_name_plural = 'SKU列表'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sku_code} - {self.sku_name}"
