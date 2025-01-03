from django.db import models
from django.utils import timezone

class Warehouse(models.Model):
    name = models.CharField('仓库名称', max_length=100)
    address = models.CharField('仓库地址', max_length=200, blank=True, null=True)
    contact = models.CharField('联系人', max_length=50, blank=True, null=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '仓库'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class Allocation(models.Model):
    AREA_TYPE_CHOICES = (
        ('normal', '普通区'),
        ('cold', '冷藏区'),
        ('frozen', '冷冻区'),
        ('dangerous', '危险品区'),
    )
    
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='仓库')
    area_code = models.CharField('货区编码', max_length=50)
    area_name = models.CharField('货区名称', max_length=100)
    area_type = models.CharField('货区类型', max_length=20, choices=AREA_TYPE_CHOICES, default='normal')
    location_code = models.CharField('货位编码', max_length=50)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '货位'
        verbose_name_plural = verbose_name
        ordering = ['warehouse', 'area_code', 'location_code']
        unique_together = ['warehouse', 'location_code']

    def __str__(self):
        return f"{self.warehouse.name} - {self.area_name} - {self.location_code}"

class Stock(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, verbose_name='仓库')
    sku = models.ForeignKey('gallery.SKU', on_delete=models.CASCADE, verbose_name='商品')
    stock_num = models.IntegerField('库存数量', default=0)
    cost = models.DecimalField('成本', max_digits=10, decimal_places=2, default=0)
    supplier = models.ForeignKey('procurement.Supplier', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='供应商')
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '库存'
        verbose_name_plural = verbose_name
        ordering = ['-updated_at']
        unique_together = ['warehouse', 'sku']

    def __str__(self):
        return f"{self.warehouse.name} - {self.sku.sku_name} - {self.stock_num}"

class StockInRecord(models.Model):
    """入库单"""
    SOURCE_TYPE_CHOICES = (
        ('purchase', '采购入库'),
        ('transfer', '调拨入库'),
        ('return', '退货入库'),
        ('other', '其他入库'),
    )
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    stock_in_no = models.CharField('入库单号', max_length=50, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='入库仓库')
    source_type = models.CharField('来源类型', max_length=20, choices=SOURCE_TYPE_CHOICES)
    source_no = models.CharField('来源单号', max_length=50)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    operator = models.CharField('操作人', max_length=50)
    remark = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '入库单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.stock_in_no

class StockInDetail(models.Model):
    """入库单明细"""
    stock_in = models.ForeignKey(
        StockInRecord,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='入库单'
    )
    sku = models.ForeignKey('gallery.SKU', on_delete=models.PROTECT, verbose_name='商品')
    quantity = models.IntegerField('数量')
    cost = models.DecimalField('成本', max_digits=10, decimal_places=2)
    allocation = models.ForeignKey(Allocation, on_delete=models.PROTECT, verbose_name='货位')
    remark = models.CharField('备注', max_length=200, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '入库单明细'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return f"{self.stock_in.stock_in_no} - {self.sku.sku_name}"

class StockOutRecord(models.Model):
    """出库单"""
    SOURCE_TYPE_CHOICES = (
        ('sale', '销售出库'),
        ('transfer', '调拨出库'),
        ('scrap', '报废出库'),
        ('other', '其他出库'),
    )
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    stock_out_no = models.CharField('出库单号', max_length=50, unique=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.PROTECT, verbose_name='出库仓库')
    source_type = models.CharField('来源类型', max_length=20, choices=SOURCE_TYPE_CHOICES)
    source_no = models.CharField('来源单号', max_length=50)
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    operator = models.CharField('操作人', max_length=50)
    remark = models.TextField('备注', blank=True, null=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '出库单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.stock_out_no

class StockOutDetail(models.Model):
    """出库单明细"""
    stock_out = models.ForeignKey(
        StockOutRecord,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='出库单'
    )
    sku = models.ForeignKey('gallery.SKU', on_delete=models.PROTECT, verbose_name='商品')
    quantity = models.IntegerField('数量')
    cost = models.DecimalField('成本', max_digits=10, decimal_places=2)
    allocation = models.ForeignKey(Allocation, on_delete=models.PROTECT, verbose_name='货位')
    remark = models.CharField('备注', max_length=200, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '出库单明细'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return f"{self.stock_out.stock_out_no} - {self.sku.sku_name}"
