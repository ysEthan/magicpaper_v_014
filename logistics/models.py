from django.db import models
from django.utils.translation import gettext_lazy as _

class Carrier(models.Model):
    """物流服务商"""
    name = models.CharField('服务商名称', max_length=100)
    code = models.CharField('服务商代码', max_length=50, unique=True)
    website = models.URLField('官网', blank=True)
    tracking_url = models.URLField('跟踪链接', blank=True, help_text='使用{tracking_no}作为跟踪号占位符')
    is_active = models.BooleanField('启用状态', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '物流服务商'
        verbose_name_plural = '物流服务商'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_tracking_url(self, tracking_no):
        """获取跟踪链接"""
        if self.tracking_url and tracking_no:
            return self.tracking_url.replace('{tracking_no}', tracking_no)
        return ''

class Service(models.Model):
    """物流服务"""
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE,
        verbose_name='服务商'
    )
    name = models.CharField('服务名称', max_length=100)
    code = models.CharField('服务代码', max_length=50)
    description = models.TextField('服务说明', blank=True)
    estimated_days = models.IntegerField('预计天数', default=0)
    base_fee = models.DecimalField('基础费用', max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField('启用状态', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '物流服务'
        verbose_name_plural = '物流服务'
        ordering = ['carrier', 'name']
        unique_together = ['carrier', 'code']

    def __str__(self):
        return f"{self.carrier.name} - {self.name}"

class Package(models.Model):
    """包裹信息"""
    class PackageStatus(models.TextChoices):
        PENDING = 'pending', _('待发货')
        SHIPPED = 'shipped', _('已发货')
        DELIVERED = 'delivered', _('已送达')
        RETURNED = 'returned', _('已退回')
        LOST = 'lost', _('已丢失')

    order = models.ForeignKey(
        'trade.Order',
        on_delete=models.CASCADE,
        verbose_name='订单'
    )
    warehouse = models.ForeignKey(
        'storage.Warehouse',
        on_delete=models.PROTECT,
        verbose_name='发货仓库'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        verbose_name='物流服务'
    )
    tracking_no = models.CharField('跟踪号', max_length=100, blank=True)
    status = models.CharField(
        '包裹状态',
        max_length=20,
        choices=PackageStatus.choices,
        default=PackageStatus.PENDING
    )
    shipping_fee = models.DecimalField('运费', max_digits=10, decimal_places=2, default=0)
    weight = models.DecimalField('重量(kg)', max_digits=10, decimal_places=2, default=0)
    length = models.DecimalField('长(cm)', max_digits=10, decimal_places=2, default=0)
    width = models.DecimalField('宽(cm)', max_digits=10, decimal_places=2, default=0)
    height = models.DecimalField('高(cm)', max_digits=10, decimal_places=2, default=0)
    items = models.JSONField('包裹物品', default=list)
    shipping_label = models.FileField('面单文件', upload_to='shipping_labels/', blank=True)
    shipped_at = models.DateTimeField('发货时间', null=True, blank=True)
    delivered_at = models.DateTimeField('送达时间', null=True, blank=True)
    tracking_info = models.JSONField('跟踪信息', default=list)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '包裹'
        verbose_name_plural = '包裹'
        ordering = ['-created_at']

    def __str__(self):
        return f"订单 {self.order.order_no} 的包裹"

    def get_tracking_url(self):
        """获取跟踪链接"""
        return self.service.carrier.get_tracking_url(self.tracking_no)

    def get_volume_weight(self):
        """计算体积重"""
        return (self.length * self.width * self.height) / 6000

    def get_charged_weight(self):
        """获取计费重量"""
        volume_weight = self.get_volume_weight()
        return max(volume_weight, self.weight)

class PackageStatusLog(models.Model):
    """包裹状态变更记录"""
    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        verbose_name='包裹'
    )
    from_status = models.CharField(
        '原状态',
        max_length=20,
        choices=Package.PackageStatus.choices
    )
    to_status = models.CharField(
        '新状态',
        max_length=20,
        choices=Package.PackageStatus.choices
    )
    remark = models.CharField('备注', max_length=200, blank=True)
    operator = models.ForeignKey(
        'auth.User',
        on_delete=models.PROTECT,
        verbose_name='操作人'
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)

    class Meta:
        verbose_name = '包裹状态记录'
        verbose_name_plural = '包裹状态记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.package} 状态从 {self.get_from_status_display()} 变更为 {self.get_to_status_display()}"
