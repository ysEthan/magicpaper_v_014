# Generated by Django 4.2.16 on 2025-01-03 16:27

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseOrder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order_no', models.CharField(max_length=50, unique=True, verbose_name='采购单号')),
                ('purchase_date', models.DateField(verbose_name='采购日期')),
                ('expected_date', models.DateField(verbose_name='预计到货日期')),
                ('status', models.CharField(choices=[('draft', '草稿'), ('confirmed', '已确认'), ('received', '已收货'), ('completed', '已完成'), ('cancelled', '已取消')], default='draft', max_length=20, verbose_name='状态')),
                ('total_amount', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='总金额')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '采购单',
                'verbose_name_plural': '采购单',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Supplier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='供应商名称')),
                ('contact', models.CharField(blank=True, max_length=50, null=True, verbose_name='联系人')),
                ('contact_phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='联系电话')),
                ('address', models.CharField(blank=True, max_length=200, null=True, verbose_name='地址')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
            ],
            options={
                'verbose_name': '供应商',
                'verbose_name_plural': '供应商',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PurchaseOrderDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.IntegerField(verbose_name='数量')),
                ('unit_price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='单价')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='金额')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='更新时间')),
                ('purchase_order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='procurement.purchaseorder', verbose_name='采购单')),
                ('sku', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='gallery.sku', verbose_name='商品')),
            ],
            options={
                'verbose_name': '采购单明细',
                'verbose_name_plural': '采购单明细',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='purchaseorder',
            name='supplier',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='procurement.supplier', verbose_name='供应商'),
        ),
    ]
