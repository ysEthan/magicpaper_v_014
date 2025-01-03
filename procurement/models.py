from django.db import models
from django.utils import timezone

class Supplier(models.Model):
    name = models.CharField('供应商名称', max_length=100)
    contact = models.CharField('联系人', max_length=50, blank=True, null=True)
    contact_phone = models.CharField('联系电话', max_length=20, blank=True, null=True)
    address = models.CharField('地址', max_length=200, blank=True, null=True)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name

class PurchaseOrder(models.Model):
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('confirmed', '已确认'),
        ('received', '已收货'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )

    order_no = models.CharField('采购单号', max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    warehouse = models.ForeignKey('storage.Warehouse', on_delete=models.PROTECT, verbose_name='收货仓库')
    purchase_date = models.DateField('采购日期')
    expected_date = models.DateField('预计到货日期')
    status = models.CharField('状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    total_amount = models.DecimalField('总金额', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '采购单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.order_no

class PurchaseOrderDetail(models.Model):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='采购单'
    )
    sku = models.ForeignKey('gallery.SKU', on_delete=models.PROTECT, verbose_name='商品')
    quantity = models.IntegerField('数量')
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    amount = models.DecimalField('金额', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('创建时间', default=timezone.now)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '采购单明细'
        verbose_name_plural = verbose_name
        ordering = ['id']

    def __str__(self):
        return f"{self.purchase_order.order_no} - {self.sku.sku_name}"

    def save(self, *args, **kwargs):
        # 计算金额
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # 更新采购单总金额
        self.purchase_order.total_amount = self.purchase_order.details.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        self.purchase_order.save()
