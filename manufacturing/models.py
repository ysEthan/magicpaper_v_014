from django.db import models
from django.contrib.auth.models import User
from gallery.models import SKU

class Factory(models.Model):
    """工厂模型"""
    name = models.CharField('工厂名称', max_length=100)
    code = models.CharField('工厂代码', max_length=50, unique=True)
    contact = models.CharField('联系人', max_length=50)
    phone = models.CharField('联系电话', max_length=20)
    address = models.CharField('地址', max_length=200)
    is_active = models.BooleanField('是否启用', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '工厂'
        verbose_name_plural = '工厂列表'
        ordering = ['-created_at']
        db_table = 'manufacturing_factory'

    def __str__(self):
        return self.name

class ProductionOrder(models.Model):
    """生产订单模型"""
    class OrderType(models.TextChoices):
        SAMPLE = 'sample', '样品订单'
        MASS = 'mass', '量产订单'

    class OrderStatus(models.TextChoices):
        DRAFT = 'draft', '草稿'
        PENDING = 'pending', '待处理'
        IN_PRODUCTION = 'in_production', '生产中'
        COMPLETED = 'completed', '已完成'
        CANCELLED = 'cancelled', '已取消'

    order_no = models.CharField('订单编号', max_length=50, unique=True)
    order_type = models.CharField(
        '订单类型',
        max_length=20,
        choices=OrderType.choices,
        default=OrderType.MASS
    )
    status = models.CharField(
        '订单状态',
        max_length=20,
        choices=OrderStatus.choices,
        default=OrderStatus.DRAFT
    )
    factory = models.ForeignKey(
        Factory,
        on_delete=models.PROTECT,
        verbose_name='生产工厂',
        null=True,
        blank=True
    )
    sku = models.ForeignKey(
        SKU,
        on_delete=models.PROTECT,
        verbose_name='产品SKU'
    )
    quantity = models.IntegerField('生产数量')
    unit_price = models.DecimalField(
        '单价',
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )
    expected_date = models.DateField('预计完成日期', null=True, blank=True)
    delivery_date = models.DateField('预计交货日期', null=True, blank=True)
    creator = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='创建人',
        related_name='created_orders'
    )
    follower = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        verbose_name='跟单员',
        related_name='following_orders',
        null=True,
        blank=True
    )
    remark = models.TextField('备注', blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '生产订单'
        verbose_name_plural = '生产订单列表'
        ordering = ['-created_at']
        db_table = 'manufacturing_production_order'

    def __str__(self):
        return self.order_no

class SampleReview(models.Model):
    """样品评审记录模型"""
    production_order = models.ForeignKey(
        ProductionOrder,
        on_delete=models.CASCADE,
        verbose_name='生产订单',
        limit_choices_to={'order_type': ProductionOrder.OrderType.SAMPLE}
    )
    reviewer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name='评审人'
    )
    review_date = models.DateField('评审日期')
    content = models.TextField('评审内容')
    conclusion = models.CharField('评审结论', max_length=50)
    attachments = models.JSONField('附件列表', default=list)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '样品评审'
        verbose_name_plural = '样品评审列表'
        ordering = ['-review_date']
        db_table = 'manufacturing_sample_review'

    def __str__(self):
        return f"{self.production_order.order_no} - {self.review_date}"
