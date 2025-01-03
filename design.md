### 项目概述

本项目是一个ERP系统，主要满足供应链管理、和生产管理的需求。

项目采用了Django 框架，前端主要使用Tabler模板。

Tabler的CSS框架中的静态文件都放在了/static，已经预先创建了一些页面的HTML模版，都已放在了/templates 下

主要有以下APP ，这些APP我已经在项目中创建，但是还没有添加上任何模型和功能。

| ID   | app_name      | 功能                             |
| ---- | ------------- | -------------------------------- |
| 1    | muggle        | 主要是用户认证、权限管理，       |
| 2    | gallery       | 主要是商品管理模块               |
| 3    | manufacturing | 生产模块                         |
| 4    | procurement   | 采购模块                         |
| 5    | storage       | 库存模块                         |
| 6    | trade         | 销售模块                         |
| 7    | page          | 页面管理，主要是一些报表、展示页 |
| 8    | logistics     | 物流模块                         |

另外需要注意，这个系统的搭建，是为了取代原有的旺店通系统。

但是在业务过渡阶段，还是会需要两个系统同时操作，因此会涉及到很多业务数据双向同步的功能。

### 功能模块设计

#### 用户认证

在muggle应用中，增加用户认证相关的功能
路由使用 /muggle/*，
页面尽量使用 /templates/muggle下的现有的模板，
尽量基于/static已有的Tabler的CSS框架中的静态文件，不要改变项目原有的文件结构

我希望用户可以区分为普通用户和管理员，未登录用户、普通用户和管理员拥有不同权限。


#### 商品管理

##### 基础功能：

商品按照类目、SPU、SKU的维度来管理，首先按照以下我历史创建过的模型文件，新建相应的模型

```python
class Brand(models.Model):
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
    STATUS_CHOICES = (
        (1, '启用'),
        (0, '禁用'),
    )
    
    LEVEL_CHOICES = (
        (1, '一级分类'),
        (2, '二级分类'),
        (3, '三级分类'),
    )

    id = models.AutoField(primary_key=True, verbose_name='分类ID')
    category_name_en = models.CharField(max_length=100, verbose_name='英文名称')
    category_name_zh = models.CharField(max_length=100, verbose_name='中文名称')
    description = models.TextField(blank=True, null=True, verbose_name='分类描述')
    image = models.ImageField(
        upload_to=category_image_path, 
        blank=True, 
        null=True, 
        verbose_name='分类图片'
    )
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='children',
        verbose_name='父分类'
    )
    rank_id = models.IntegerField(default=0, verbose_name='排序ID')
    original_data = models.TextField('原始数据', blank=True, null=True)
    level = models.IntegerField(
        choices=LEVEL_CHOICES,
        default=1,
        verbose_name='分类层级'
    )
    is_last_level = models.BooleanField(
        default=False, 
        verbose_name='是否最后一级'
    )
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        default=1,
        verbose_name='状态'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'gallery_category'
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['rank_id', 'id']

    def __str__(self):
        return f"{self.category_name_zh} ({self.category_name_en})"

    def clean(self):
        if self.parent:
            if self.level <= self.parent.level:
                raise ValidationError('子类目的层级必须大于父类目的层级')
        elif self.level != 1:
            raise ValidationError('没有父类目时，必须是一级分类')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        
        if self.image and not self.image.name.startswith(f'categories/category_{self.pk}_'):
            old_path = self.image.path
            filename = os.path.basename(self.image.name)
            ext = filename.split('.')[-1]
            
            new_filename = f"category_{self.pk}_{self.category_name_en}.{ext}"
            new_path = os.path.join('categories', new_filename)
            
            self.image.name = new_path
            super().save(update_fields=['image'])
            
            if os.path.exists(old_path):
                new_full_path = os.path.join(settings.MEDIA_ROOT, new_path)
                os.makedirs(os.path.dirname(new_full_path), exist_ok=True)
                os.rename(old_path, new_full_path)

    @property
    def full_name(self):
        if self.parent:
            return f"{self.parent.full_name} > {self.category_name_zh}"
        return self.category_name_zh

class SPU(models.Model):
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
    PLATING_PROCESS_CHOICES = (
        ('none', '无电镀'),
        ('gold', '镀金'),
        ('silver', '镀银'),
        ('nickel', '镀镍'),
        ('chrome', '镀铬'),
        ('copper', '镀铜'),
        ('other', '其他'),
    )
    
    sku_code = models.CharField(max_length=50, unique=True, verbose_name='SKU编码')
    sku_name = models.CharField(max_length=100, verbose_name='SKU名称')
    spu = models.ForeignKey(SPU, on_delete=models.CASCADE, verbose_name='所属SPU', null=True)
    material = models.CharField(max_length=50, verbose_name='材质')
    color = models.CharField(max_length=50, verbose_name='颜色')
    plating_process = models.CharField(max_length=20, choices=PLATING_PROCESS_CHOICES, verbose_name='电镀工艺')
    surface_treatment = models.CharField(max_length=100, null=True, blank=True, verbose_name='表面处理')这个字段，也类似电镀工艺设置为可选，选项为做旧、滴胶、磨砂）
    weight = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name='重量(g)')
    length = models.IntegerField
    width = models.IntegerField
    height = models.IntegerField
    other_dimensions = models.CharField(max_length=25, null=True, blank=True, verbose_name='其他尺寸')
    suppliers_list = models.TextField(verbose_name='供应商列表', default='[]', blank=True)供应商信息包含供应商code,供应商商品编号，采购渠道，协商价格，是否默认供应商。
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

```

然后创建相应的列表视图，添加增删改查功能，并在左侧的菜单栏添加相应的入口。





##### 数据同步：

目前前期很多业务数据，是在原有的旺店通ERP系统上操作，所以需要通过API获取业务数据，保存到数据库。

请通过这个链接https://zsxj.yuque.com/cdy1c2/ie96h9/vi7fd9，认证阅读API文档。

请参考以下同步程序，了解签名认证、数据如何抓取，了解API获取到的数据结构。

```
import time
import json
import hashlib
import requests
import math
import os
from datetime import datetime, timedelta
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .models import SPU, SKU, Category

class ProductSync:
    def __init__(self):
        self.app_name = "mathmagic"
        self.app_key = "82be0592545283da00744b489f758f99"
        self.sid = "mathmagic"
        self.api_url = "https://openapi.qizhishangke.com/api/openservices/product/v1/getItemList"
        
    def generate_sign(self, body):
        headers = {
            'Content-Type': 'application/json'
        }

        timestamp = str(int(time.time()))
        sign_str = f"{self.app_key}appName{self.app_name}body{body}sid{self.sid}timestamp{timestamp}{self.app_key}"
        sign = hashlib.md5(sign_str.encode()).hexdigest()
        
        params = {
            "appName": self.app_name,
            "sid": self.sid,
            "sign": sign,
            "timestamp": timestamp,
        }
        return params, headers

    def sync_products(self, start_time=None, end_time=None, page=1):
        """同步产品数据"""
        print(f"开始同步第 {page} 页数据...")  # 添加调试信息
        
        if not start_time:
            # 默认同步最近7天的数据
            start_time = (datetime.now() - timedelta(days=85)).strftime('%Y-%m-%d %H:%M:%S')
        if not end_time:
            end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        print(f"同步时间范围: {start_time} 到 {end_time}")  # 添加调试信息

        body = {
            "page_size": 100,
            "page_no": page,
            "start_time": start_time,
            "end_time": end_time,
            "status": 0
        }

        body_str = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
        params, headers = self.generate_sign(body_str)

        try:
            response = requests.post(self.api_url, params=params, headers=headers, data=body_str)
            print(f"API响应状态码: {response.status_code}")  # 添加调试信息
            
            if response.status_code != 200:
                print(f"API响应内容: {response.text}")  # 添加调试信息
                raise Exception(f"API请求失败: {response.text}")

            result = response.json()
            if result['code'] != 200:
                raise Exception(f"业务处理失败: {result['message']}")

            data = result['data']
            total = data['total']
            page_size = data['pageSize']
            current_page = data['currentPage']
            max_page = math.ceil(total / page_size)

            # 处理当前页的数据
            synced_count = self._process_products(data['data'])

            # 如果还有下一页，递归处理
            if current_page < max_page :
                time.sleep(1)  # 避免请求过快
                next_count = self.sync_products(start_time, end_time, page + 1)
                synced_count += next_count

            return synced_count

        except Exception as e:
            print(f"发生异常: {str(e)}")  # 添加调试信息
            raise

    def _download_image(self, image_url, sku_code):
        """下载图片"""
        try:
            print(f"开始下载图片: {image_url}")
            
            # 添加请求头，模拟浏览器行为
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(image_url, headers=headers, timeout=30)
            if response.status_code == 200:
                # 检查内容类型
                content_type = response.headers.get('content-type', '')
                if not content_type.startswith('image/'):
                    print(f"非图片内容类型: {content_type}")
                    return None
                    
                # 生成文件名
                ext = image_url.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'gif']:
                    ext = 'jpg'
                filename = f"skus/{sku_code}.{ext}"  # 确保这个路径与 MEDIA_ROOT 相对应
                
                try:
                    # 删除旧图片
                    storage = default_storage
                    if storage.exists(filename):
                        storage.delete(filename)
                    
                    # 保存新图片
                    path = default_storage.save(filename, ContentFile(response.content))
                    print(f"图片保存成功: {path}")
                    return path
                except Exception as e:
                    print(f"保存图片失败: {str(e)}")
                    return None
            else:
                print(f"下载图片失败: HTTP {response.status_code}")
                print(f"响应内容: {response.text[:200]}")  # 只打印前200个字符
                return None
            
        except requests.exceptions.Timeout:
            print(f"下载图片超时: {image_url}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"请求图片失败: {str(e)}")
            return None
        except Exception as e:
            print(f"下载图片异常: {str(e)}")
            return None

    def _process_products(self, products):
        """处理产品数据"""
        synced_count = 0
        
        # 获取默认类目
        default_category = Category.objects.filter(is_last_level=True).first()
        if not default_category:
            raise Exception("系统中没有可用的最后一级类目，请先创建类目")
        
        for product in products:
            try:
                print(f"开始处理产品: {product['specNo']}")
                
                # 根据 className 查找对应的类目
                category = default_category  # 默认类目
                if product.get('className'):
                    try:
                        # 将中文类目名转换为英文格式（去除空格，转小写）
                        class_name_en = product['className'].replace(' ', '').lower()
                        # 尝试通过英文名称匹配类目
                        category = Category.objects.filter(
                            category_name_en__iexact=class_name_en,  # 不区分大小写匹配
                        ).first() or default_category
                        
                        if category == default_category:
                            print(f"未找到类目 {product['className']}({class_name_en})，使用默认类目")
                    except Category.DoesNotExist:
                        print(f"未找到类目 {product['className']}，使用默认类目")
                
                # 处理SPU
                spu_defaults = {
                    'spu_name': product['goodsName'],
                    'status': True,
                    'category': category,  # 使用匹配到的类目
                }
                
                try:
                    spu = SPU.objects.get(spu_code=product['goodsNo'])
                    # 如果 SPU 已存在，不更新类目
                    spu_defaults['category'] = spu.category
                except SPU.DoesNotExist:
                    pass
                
                spu, created = SPU.objects.update_or_create(
                    spu_code=product['goodsNo'],
                    defaults=spu_defaults
                )
                print(f"SPU {'创建' if created else '更新'} 成功: {spu.spu_code}")

                # 处理SKU
                sku_defaults = {
                    'sku_name': product['specName'],
                    'plating_process': product['prop4'] or 'none',  # 电镀工艺，如果为空则为'none'
                    'color': product['prop2'] or '无',  # 颜色
                    'material': product['prop8'] or '无',  # 材质
                    'length': float(product['length']) if product['length'] else 0,
                    'width': float(product['width']) if product['width'] else 0,
                    'height': float(product['height']) if product['height'] else 0,
                    'weight': float(product['weight']) if product['weight'] else 0,
                    'status': True,
                    'spu': spu,
                    # 将供应商信息存储在suppliers_list中
                    'suppliers_list': json.dumps([{
                        'code': p['providerNo'],
                        'name': p['providerName']
                    } for p in product['providerList']]) if product['providerList'] else '[]'
                }

                # 处理图片
                if product.get('imgUrl'):
                    image_url = product['imgUrl']
                    print(f"发现图片URL: {image_url}")
                    # 移除时间戳参数
                    image_url = image_url.split('?')[0]
                    image_path = self._download_image(image_url, product['specNo'])
                    if image_path:
                        sku_defaults['img_url'] = image_path

                sku, created = SKU.objects.update_or_create(
                    sku_code=product['specNo'],
                    defaults=sku_defaults
                )
                print(f"SKU {'创建' if created else '更新'} 成功: {sku.sku_code}")
                
                synced_count += 1

            except Exception as e:
                print(f"处理产品数据失败: {str(e)}, 产品: {product['specNo']}")
                print(f"错误详情: {type(e).__name__}")
                print(f"产品数据: {product}")
                continue

        return synced_count

    def clean_old_images(self, days=30):
        """清理指定天数之前的旧图片"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            storage = default_storage
            directory = 'skus/'
            
            # 获取目录中的所有文件
            _, files = storage.listdir(directory)
            
            for filename in files:
                try:
                    path = os.path.join(directory, filename)
                    # 获取文件的修改时间
                    modified_time = datetime.fromtimestamp(storage.get_modified_time(path).timestamp())
                    
                    # 如果文件超过指定天数且不是当前使用的图片，则删除
                    if modified_time < cutoff_date:
                        # 检查是否有SKU正在使用这个图片
                        if not SKU.objects.filter(img_url=path).exists():
                            storage.delete(path)
                            print(f"删除旧图片: {path}")
                            
                except Exception as e:
                    print(f"处理文件时出错 {filename}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"清理旧图片时出错: {str(e)}") 
```

现在，请帮我实现数据同步功能，

​	1，通过API 获取sku 列表

​	2，提取SPU相关信息，判断模型数据库中是否已经存在，不如不存在则直接新增。

​	3，保存SKU数据。

请在SKU列表页面，帮我增加一个按钮，通过点击按钮会触发同步。



##### SKU新增：

SKU新增，是一个高频且非常耗人力的事情，我希望通过优化页面交互和数据的自动填充，来提供资料录入的效率。

首先请仔细阅读\templates\gallery\sku_form.html，这是我初步设计的一个页面。

因为SKU跟SPU是一对多的关联关系，也及SKU属于SPU,SPU可能包含多个SKU

所以在录入数据的时候，页面上要支持两种录入方式，

​	当要新增的SKU，不属于现有的Spu时，以填写的SPU数据直接新建。

​	当要新增的SKU，归属于现有的某个SPU是，可以直接通过输入框搜索，然后下拉选中。

部分数据的录入做一下优化处理：

​	比如长宽高、其他尺寸、重量前端页面允许不输入，不输入时默认保存为0，模型上保持不允许为空。

​	比如材质、颜色、电镀工艺、表面处理，前端页面允许不输入，不输入时默认保存"无"

供应商的部分，请注意供应商有可能存在多个，因此我用json列表的方式来保存数据。所以在录入的时候，供应商部分的信息，请拆分多个输入框。参考一下图片的录入方式，	![image-20250102220622805](C:\Users\75781\AppData\Roaming\Typora\typora-user-images\image-20250102220622805.png)

用户可以点下按钮，增加一列

在不同的输入框，录入相应的信息，每列信息，以一个json元素，保存到数据库中。

图片的录入，我希望图片支持本地文件上传和拍照上传两种方式，按钮可以适当做的大一些，当点击拍照上传时，会自动调用高拍仪，进行拍照上传。

最后是数据的同步，我希望新的SKU创建完成，或者编辑保存后，也可以同步到旧有的旺店通ERP系统中。

请查看相应的API文档：https://zsxj.yuque.com/cdy1c2/ie96h9/qn56suyggdqgmw4l，通过推送单品接口，实现数据的同步推送。





#### 采购管理

##### 基础功能

​	采购功能涵盖供应商管理、采购单处理、采购数据分析，实现对供应商的筛选评估、采购流程全程管控。

​	请帮我创建相应的模型，主要是供应商、采购主单、采购明细，以及其他必要的模型。

​	模型的字段，请参考以下我创建过的模型文件:	

```python
from django.db import models
from django.utils import timezone
from gallery.models import SKU


class Supplier(models.Model):
    """供应商信息表"""
    name = models.CharField('供应商名称', max_length=100)
    contact_info = models.CharField('联系方式', max_length=100)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '供应商'
        verbose_name_plural = verbose_name


class PurchaseOrder(models.Model):
    """采购单主表"""
    class Status(models.IntegerChoices):
        DRAFT = 0, '草稿'
        PENDING_ORDER = 1, '待下单'
        PENDING_PAYMENT = 2, '待支付'
        PENDING_STORAGE = 3, '待入库'
        STORED = 4, '已入库'
        CANCELLED = 5, '已取消'

    purchase_order_number = models.CharField('采购单号', max_length=50, unique=True)
    supplier = models.ForeignKey(Supplier, on_delete=models.PROTECT, verbose_name='供应商')
    warehouse = models.ForeignKey('storage.Warehouse', on_delete=models.PROTECT, null=True, blank=True, verbose_name='仓库')
    purchase_date = models.DateField('采购日期')
    status = models.IntegerField('采购状态', choices=Status.choices, default=Status.DRAFT)
    expected_delivery_date = models.DateField('预计到货日期')
    total_amount = models.DecimalField('总金额', max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def __str__(self):
        return self.purchase_order_number

    class Meta:
        verbose_name = '采购单'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']


class PurchaseOrderDetail(models.Model):
    """采购单明细表"""
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, verbose_name='采购单')
    product = models.ForeignKey(SKU, on_delete=models.PROTECT, verbose_name='产品')
    quantity = models.DecimalField('采购数量', max_digits=10, decimal_places=2)
    unit_price = models.DecimalField('单价', max_digits=10, decimal_places=2)
    amount = models.DecimalField('金额', max_digits=10, decimal_places=2)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    def save(self, *args, **kwargs):
        # 计算金额
        self.amount = self.quantity * self.unit_price
        super().save(*args, **kwargs)
        
        # 更新采购单总金额
        total = self.purchase_order.purchaseorderdetail_set.aggregate(
            total=models.Sum('amount'))['total'] or 0
        self.purchase_order.total_amount = total
        self.purchase_order.save()

    def __str__(self):
        return f"{self.purchase_order.purchase_order_number} - {self.product.name}"

    class Meta:
        verbose_name = '采购单明细'
        verbose_name_plural = verbose_name

```

​	

以及采购单数据的API接口文档：https://zsxj.yuque.com/cdy1c2/ie96h9/hb57txolc0ne20l1

模型创建之后，再创建相应的列表，增删改查功能。

采购单的列表，我希望以页签的形式来展示，不同的页面可以看到不同状态的采购单列表。

注意给列表加上分页的功能

##### 数据同步

​	采购单数据，也需要从旺店通ERP系统拉取，请仔细阅读API文档https://zsxj.yuque.com/cdy1c2/ie96h9/hb57txolc0ne20l1。请参考我历史写的同步代码：

```python
import time
import hashlib
import json
import math
import requests
from datetime import datetime, timedelta
from django.utils import timezone
from .models import PurchaseOrder, PurchaseOrderDetail, Supplier
from gallery.models import SKU
from storage.models import Warehouse

def generate_sign(body):
    """生成API签名"""
    appName = "mathmagic"
    appKey = "82be0592545283da00744b489f758f99"
    sid = "mathmagic"

    headers = {
        'Content-Type': 'application/json'
    }

    timestamp = str(int(time.time()))
    sign_str = "{appKey}appName{appName}body{body}sid{sid}timestamp{timestamp}{appKey}".format(
        appKey=appKey, appName=appName, body=body, sid=sid, timestamp=timestamp
    )
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    
    params = {
        "appName": appName,
        "sid": sid,
        "sign": sign,
        "timestamp": timestamp,
    }
    return params, headers

def sync_purchase_data(response_data):
    """同步采购单数据"""
    if response_data.get('code') != 200:
        raise Exception(f"API返回错误: {response_data.get('message')}")
        
    data = response_data.get('data', {})
    items = data.get('data', [])
    
    # 按采购单号分组
    purchase_orders = {}
    for item in items:
        purchase_no = item.get('purchaseNo')
        if purchase_no not in purchase_orders:
            purchase_orders[purchase_no] = {
                'main': item,
                'details': []
            }
        purchase_orders[purchase_no]['details'].append(item)
    
    # 处理每个采购单
    for purchase_no, order_data in purchase_orders.items():
        try:
            main_data = order_data['main']
            print(f"\n处理采购单: {purchase_no}")
            
            # 获取或创建供应商
            supplier_data = {
                'name': main_data.get('providerName'),
                'contact_info': main_data.get('providerNo', '')
            }
            supplier, _ = Supplier.objects.get_or_create(
                name=supplier_data['name'],
                defaults=supplier_data
            )
            
            # 获取仓库
            warehouse = None
            warehouse_id = main_data.get('warehouseId')
            if warehouse_id:
                try:
                    warehouse = Warehouse.objects.get(id=warehouse_id)
                except Warehouse.DoesNotExist:
                    print(f"仓库不存在: {warehouse_id}")
            
            # 处理状态
            status_mapping = {
                '草稿': PurchaseOrder.Status.DRAFT,
                '待下单': PurchaseOrder.Status.PENDING_ORDER,
                '待支付': PurchaseOrder.Status.PENDING_PAYMENT,
                '待入库': PurchaseOrder.Status.PENDING_STORAGE,
                '已完成': PurchaseOrder.Status.STORED,
                '已作废': PurchaseOrder.Status.CANCELLED
            }
            status = status_mapping.get(main_data.get('status'), PurchaseOrder.Status.DRAFT)
            
            # 创建或更新采购单
            purchase_order_data = {
                'supplier': supplier,
                'warehouse': warehouse,
                'purchase_date': parse_datetime(main_data.get('created')).date() if main_data.get('created') else None,
                'status': status,
                'expected_delivery_date': parse_datetime(main_data.get('tradeTime')).date() if main_data.get('tradeTime') else None,
            }
            
            purchase_order, created = PurchaseOrder.objects.update_or_create(
                purchase_order_number=purchase_no,
                defaults=purchase_order_data
            )
            print(f"{'创建' if created else '更新'}采购单: {purchase_order}")
            
            # 处理采购单明细
            for detail in order_data['details']:
                try:
                    # 获取SKU
                    sku = SKU.objects.get(sku_code=detail['specNo'])
                    
                    # 处理价格和数量
                    price_str = detail.get('price', '').replace('CNY ', '')
                    quantity = float(detail.get('num', 0))
                    unit_price = float(price_str) if price_str else 0
                    
                    # 创建或更新采购单明细
                    detail_data = {
                        'purchase_order': purchase_order,
                        'product': sku,
                        'quantity': quantity,
                        'unit_price': unit_price,
                        'amount': quantity * unit_price
                    }
                    
                    detail_obj, detail_created = PurchaseOrderDetail.objects.update_or_create(
                        purchase_order=purchase_order,
                        product=sku,
                        defaults=detail_data
                    )
                    print(f"{'创建' if detail_created else '更新'}采购单明细: {detail_obj}")
                    
                except SKU.DoesNotExist:
                    print(f"SKU不存在: {detail.get('specNo')}")
                except Exception as e:
                    print(f"处理采购单明细时出错: {str(e)}")
                    print(f"明细数据: {detail}")
                    raise
                    
        except Exception as e:
            print(f"处理采购单时出错: {str(e)}")
            print(f"采购单数据: {main_data}")
            raise
            
    return True, "采购单数据同步完成"

def sync_all_purchase():
    """同步所有采购单数据"""
    try:
        # 准备时间范围
        end_date = timezone.now()
        start_date = end_date - timedelta(days=25)
        
        start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
        end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
        
        # 准备请求数据
        body = {
            "pageSize": 200,
            "pageNo": 1,
            "createTimeBegin": start_date_str,
            "createTimeEnd": end_date_str,
            "orderStatus": [40, 42, 75, 70, 10],  # 待下单 待支付 待入库 已完成 已作废
            "account": "admin"
        }
        
        body_str = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
        params, headers = generate_sign(body_str)
        
        # 发送API请求
        url = "https://openapi.qizhishangke.com/api/openservices/purchaseOrder/v1/getOrders"
        print(f"请求API: {url}")
        print(f"请求参数: {body_str}")
        
        response = requests.post(url, params=params, headers=headers, data=body_str.encode('utf-8'))
        print(f"API响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            raise Exception(f"API请求失败: {response.text}")
            
        response_data = response.json()
        success, message = sync_purchase_data(response_data)
        
        if success:
            return True, f"采购单同步成功: {message}"
        else:
            return False, f"采购单同步失败: {message}"
            
    except Exception as e:
        print(f"同步采购单时出错: {str(e)}")
        return False, str(e) 
```

帮我实现采购单数据的同步功能，获取采购单数据，保存到采购单主单和采购单明细。





#### 库存管理

##### 基础功能

​	库存管理功能主要是入库、出库、和库存管理。我希望通过批次管理，实现先进先出(FIFO)的逻辑。

​	每一次入库，都单独创建一条入库明细(每一条入库记录就相当于一个批次)，同时也新增一条库存记录。这样可以清楚的记录每一批库存的入库信息。而入库信息一般与采购单或者调拨单，或者其他类型的入库业务关联，可以记录下每次入库的成本，这样我们就可以通过批次，获取到每一批库存的成本。注意，这里的成本，我们用固定成本法记录，而不是移动加权平均。

​	每一次的出库，都会按照先进先出的原则，找到最早的，但库存数大于0的库存记录，更新减去出库数量，如果该批次的数量小于应出库的数量，就好到次早的批次扣减。

​	这样我们就可以实现先进先出，也可以实现库存成本的统计，每一笔出库记录的成本核算。

​	首先请帮我创建相应的模型，主要是仓库、货位、库存、入库记录、出库记录，以及其他需要用到的模型。

​	模型的字段，请参考出入库明细数据的API接口文档：https://zsxj.yuque.com/cdy1c2/ie96h9/fy76x4#QxdJZ；以及以下我创建过的模型文件:	

```python
from django.db import models
from django.core.validators import MinValueValidator
from gallery.models import SKU
from procurement.models import PurchaseOrderDetail

class Warehouse(models.Model):
    """仓库模型"""
    
    id = models.AutoField(
        primary_key=True,
        verbose_name='仓库ID'
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='仓库名称'
    )
    
    address = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='仓库地址'
    )
    
    contact = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='联系人'
    )
    
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='联系电话'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'storage_warehouse'
        verbose_name = '仓库'
        verbose_name_plural = '仓库列表'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Allocation(models.Model):
    """货区货位模型"""
    
    class AreaType(models.TextChoices):
        NORMAL = 'NORMAL', '普通区'
        CONSUMABLE = 'CONSUMABLE', '耗材区'
        REQUISITION = 'REQUISITION', '领用区'
    
    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.CASCADE,
        verbose_name='所属仓库'
    )
    
    area_code = models.CharField(
        max_length=10,
        verbose_name='货区编码'
    )
    
    area_name = models.CharField(
        max_length=20,
        verbose_name='货区名称'
    )
    
    area_type = models.CharField(
        max_length=20,
        choices=AreaType.choices,
        default=AreaType.NORMAL,
        verbose_name='货区类型'
    )
    
    location_code = models.CharField(
        max_length=10,
        verbose_name='货位编码'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'storage_allocation'
        verbose_name = '货区货位'
        verbose_name_plural = '货区货位列表'
        ordering = ['warehouse', 'area_code', 'location_code']
        unique_together = ['warehouse', 'area_code', 'location_code']

    def __str__(self):
        return f"{self.warehouse.name} - {self.area_name} - {self.location_code}"

class Stock(models.Model):
    """库存模型"""
    
    id = models.AutoField(
        primary_key=True,
        verbose_name='库存ID'
    )
    
    stock_num = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='库存数量'
    )
    
    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.CASCADE,
        verbose_name='所属仓库'
    )
    
    sku = models.ForeignKey(
        SKU,
        on_delete=models.CASCADE,
        verbose_name='关联SKU'
    )
    
    stockin_detail = models.OneToOneField(
        'StockInDetail',
        on_delete=models.PROTECT,
        related_name='stock',
        null=True,
        blank=True,
        verbose_name='入库明细'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'storage_stock'
        verbose_name = '库存'
        verbose_name_plural = '库存列表'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['sku']),
            models.Index(fields=['warehouse']),
        ]

    def __str__(self):
        return f"{self.warehouse.name} - {self.sku.sku_code} - {self.stock_num}"
        
    @property
    def supplier(self):
        """获取供应商"""
        if self.stockin_detail.purchase_order_detail:
            return self.stockin_detail.purchase_order_detail.purchase_order.supplier
        return None
        
    @property
    def cost(self):
        """获取成本"""
        return self.stockin_detail.cost_price

class StockInRecord(models.Model):
    """入库记录模型"""
    
    id = models.AutoField(
        primary_key=True,
        verbose_name='入库记录ID'
    )
    
    stockin_no = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='入库单号'
    )
    
    warehouse = models.ForeignKey(
        'Warehouse',
        on_delete=models.PROTECT,
        verbose_name='入库仓库'
    )
    
    src_order_no = models.CharField(
        max_length=50,
        verbose_name='来源单号'
    )
    
    src_order_type = models.IntegerField(
        choices=[
            (1, '采购入库'),
            (2, '调拨入库'),
        ],
        verbose_name='来源单据类型'
    )
    
    operator = models.CharField(
        max_length=50,
        verbose_name='操作人'
    )
    
    check_time = models.DateTimeField(
        verbose_name='审核时间'
    )
    
    status = models.IntegerField(
        choices=[
            (80, '已完成'),
        ],
        default=80,
        verbose_name='状态'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'storage_stockin_record'
        verbose_name = '入库记录'
        verbose_name_plural = '入库记录列表'
        ordering = ['-created_at']

    def __str__(self):
        return self.stockin_no

class StockInDetail(models.Model):
    """入库明细模型"""
    
    id = models.AutoField(
        primary_key=True,
        verbose_name='入库明细ID'
    )
    
    stockin_record = models.ForeignKey(
        StockInRecord,
        on_delete=models.CASCADE,
        related_name='details',
        verbose_name='入库记录'
    )
    
    sku = models.ForeignKey(
        'gallery.SKU',
        on_delete=models.PROTECT,
        verbose_name='商品SKU'
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='入库数量'
    )
    
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name='入库成本'
    )
    
    allocation = models.ForeignKey(
        'Allocation',
        on_delete=models.PROTECT,
        verbose_name='货位'
    )
    
    purchase_order_detail = models.ForeignKey(
        'procurement.PurchaseOrderDetail',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name='采购明细'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        db_table = 'storage_stockin_detail'
        verbose_name = '入库明细'
        verbose_name_plural = '入库明细列表'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.stockin_record.stockin_no} - {self.sku.sku_code}"

```

​	模型创建之后，再创建相应的列表，以及仓库和货位的增删改查功能，库存、入库记录、和出库记录不需要增删改，只需要列表和查询搜索即可。

​	注意个列表加上分页的功能。

##### 数据同步

​	库存的数据，也需要从API接口来获取，不过，我们只需要获取到出入库的明细，再基于出入库数据自行统计库存即可。

​	首先我们先获取并处理入库数据，请参考API文档链接：https://zsxj.yuque.com/cdy1c2/ie96h9/fy76x4#QxdJZ；每一条入库记录，都通过业务单号，查询到对应的采购明细，保存到入库记录中，并在库存主表新增一条库存记录。

​	可以参考我历史写过的同步代码，注意这段代码可能会有以下错误，参考大概得逻辑即可	

```python
import json
import requests
import math
import time
import hashlib
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from .models import Stock, Warehouse, StockInRecord, StockInDetail, Batch, Allocation
from gallery.models import SKU



def generate_sign(body):
    """生成API签名"""
    try:
        app_name = "mathmagic"
        app_key = "82be0592545283da00744b489f758f99"
        sid = "mathmagic"
        
        headers = {
            'Content-Type': 'application/json'
        }
        
        timestamp = str(int(time.time()))
        sign_str = f"{app_key}appName{app_name}body{body}sid{sid}timestamp{timestamp}{app_key}"
        sign = hashlib.md5(sign_str.encode()).hexdigest()
        
        params = {
            "appName": app_name,
            "sid": sid,
            "sign": sign,
            "timestamp": timestamp,
        }
        logger.info(f"生成签名成功: params={params}")
        return params, headers
    except Exception as e:
        logger.error(f"生成签名失败: {str(e)}")
        raise

def sync_stockin_data(start_date, end_date, page=1):
    """同步入库单数据"""
    try:
        print(f"开始同步第 {page} 页入库数据")
        body = {
            "start_time":"2025-01-02 00:00:00",
            "end_time":end_date,
            "status":1,
            "pageNo":1,
            "pageSize":50
        }
        
        body_str = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
        params, headers = generate_sign(body_str)
        url = "https://openapi.qizhishangke.com/api/openservices/stock/v1/getStockInOrderDetails"
        
        logger.info(f"请求参数: url={url}, params={params}, body={body_str}")
        
        # 添加重试机制
        response = None
        for attempt in range(3):
            try:
                logger.info(f"尝试第 {attempt + 1} 次请求API")
                response = requests.post(url, params=params, headers=headers, data=body_str.encode('utf-8'))
                logger.info(f"API响应状态码: {response.status_code}")
                # logger.info(f"API响应内容: {response.text[:1000]}")  # 只打印前1000个字符，避免日志过大
                break
            except Exception as e:
                logger.error(f"API请求失败 (尝试 {attempt + 1}): {str(e)}")
                if attempt < 2:
                    time.sleep(15)
                    continue
                raise
        
        if not response:
            raise Exception("API请求失败: 未获得响应")
            
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            logger.error(f"API响应解析失败: {str(e)}, 响应内容: {response.text[:1000]}")
            raise Exception(f"API响应解析失败: {str(e)}")
            
        if not isinstance(data, dict):
            logger.error(f"API响应格式错误: 预期为字典，实际为 {type(data)}, 响应内容: {data}")
            raise Exception("API响应格式错误: 不是有效的JSON对象")
            
        if 'code' not in data:
            logger.error(f"API响应缺少code字段: {data}")
            raise Exception("API响应格式错误: 缺少code字段")
            
        if data['code'] != 200:
            error_msg = data.get('message', '未知错误')
            logger.error(f"API返回错误: code={data['code']}, message={error_msg}")
            raise Exception(f"API返回错误: {error_msg}")
        
        if 'data' not in data:
            logger.error(f"API响应缺少data字段: {data}")
            raise Exception("API响应格式错误: 缺少data字段")
            
        result = data['data']
        if not isinstance(result, dict):
            logger.error(f"API响应data字段格式错误: 预期为字典，实际为 {type(result)}, 内容: {result}")
            raise Exception("API响应格式错误: data字段不是有效的JSON对象")
            
        required_fields = ['data', 'total', 'currentPage', 'pageSize']
        missing_fields = [field for field in required_fields if field not in result]
        if missing_fields:
            logger.error(f"API响应缺少必要字段: {missing_fields}, 响应内容: {result}")
            raise Exception(f"API响应格式错误: 缺少必要字段 {', '.join(missing_fields)}")
        
        logger.info(f"成功获取数据: 总数={result['total']}, 当前页={result['currentPage']}")
        
        return {
            'items': result['data'],
            'total': result['total'],
            'current_page': result['currentPage'],
            'max_page': math.ceil(result['total'] / result['pageSize'])
        }
    except Exception as e:
        logger.error(f"同步数据失败: {str(e)}")
        raise

def update_stockin_data(stockin_data):
    """更新入库单数据到数据库"""
    try:
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        # 定义允许同步的仓库ID列表
        ALLOWED_WAREHOUSE_IDS = [8, 9, 10]
        
        for item in stockin_data['items']:
            try:
                # 检查仓库ID是否在允许列表中
                if item['warehouseId'] not in ALLOWED_WAREHOUSE_IDS:
                    print(f"跳过非目标仓库的入库单: {item['stockinNo']} (仓库ID: {item['warehouseId']})")
                    skipped_count += 1
                    continue
                    
                with transaction.atomic():
                    # 检查入库单是否已存在
                    if StockInRecord.objects.filter(stockin_no=item['stockinNo']).exists():
                        print(f"入库单已存在，跳过: {item['stockinNo']}")
                        skipped_count += 1
                        continue
                    
                    # 获取或创建仓库
                    warehouse, _ = Warehouse.objects.get_or_create(
                        id=item['warehouseId'],
                        defaults={
                            'name': item['warehouseName']
                        }
                    )
                    
                    print(f"处理入库单: {item['stockinNo']} (仓库: {warehouse.name})")
                    
                    # 创建入库单记录
                    stockin_record = StockInRecord.objects.create(
                        stockin_no=item['stockinNo'],
                        warehouse=warehouse,
                        src_order_no=item['srcOrderNo'],
                        src_order_type=item['srcOrderType'],
                        operator=item['operatorName'],
                        check_time=datetime.strptime(item['checkTime'], "%Y-%m-%d %H:%M:%S"),
                        status=item['orderStatus']
                    )
                    
                    # 处理入库明细
                    details_success = True
                    details_count = 0
                    for detail in item['stockInOrderDetailsVOList']:
                        try:
                            # 获取SKU
                            try:
                                sku = SKU.objects.get(sku_code=detail['specNo'])
                            except SKU.DoesNotExist:
                                print(f"SKU不存在，跳过: {detail['specNo']}")
                                details_success = False
                                continue
                            
                            # 获取或创建货位
                            allocation, _ = Allocation.objects.get_or_create(
                                warehouse=warehouse,
                                location_code=detail['positionNo'],
                                defaults={
                                    'area_code': detail['positionNo'].split('-')[0],
                                    'area_name': f"{detail['positionNo'].split('-')[0]}区",
                                }
                            )
                            
                            # 如果是采购入库，尝试获取采购明细
                            purchase_order_detail = None
                            if item['srcOrderType'] == 1:  # 采购入库
                                from procurement.models import PurchaseOrderDetail
                                try:
                                    print(f"查找采购明细: 采购单号={item['srcOrderNo']}, SKU={sku.sku_code}")
                                    purchase_order_detail = PurchaseOrderDetail.objects.get(
                                        purchase_order__purchase_order_number=item['srcOrderNo'],
                                        product__sku_code=sku.sku_code  # 使用sku_code而不是product对象
                                    )
                                    final_cost_price = purchase_order_detail.unit_price
                                    print(f"找到采购明细: ID={purchase_order_detail.id}, 单价={final_cost_price}")
                                except PurchaseOrderDetail.DoesNotExist:
                                    print(f"采购明细不存在: {item['srcOrderNo']} - {sku.sku_code}")
                                    final_cost_price = float(detail.get('costPrice', 0))
                                    print(f"使用API成本价: {final_cost_price}")
                            else:
                                final_cost_price = float(detail.get('costPrice', 0))
                                print(f"使用API成本价: {final_cost_price}")
                            
                            # 创建入库明细
                            stockin_detail = StockInDetail.objects.create(
                                stockin_record=stockin_record,
                                sku=sku,
                                quantity=detail['num'],
                                cost_price=final_cost_price,
                                allocation=allocation,
                                purchase_order_detail=purchase_order_detail
                            )
                            
                            # 创建库存记录
                            Stock.objects.create(
                                warehouse=warehouse,
                                sku=sku,
                                stock_num=detail['num'],
                                stockin_detail=stockin_detail
                            )
                            
                            details_count += 1
                            
                        except Exception as detail_e:
                            print(f"处理入库明细失败: {str(detail_e)}")
                            details_success = False
                            continue
                    
                    if details_success and details_count > 0:
                        print(f"入库单处理成功: {item['stockinNo']}, 处理了 {details_count} 条明细")
                        success_count += 1
                    else:
                        print(f"入库单处理完成但有错误: {item['stockinNo']}, 处理了 {details_count} 条明细")
                        error_count += 1
                    
            except Exception as e:
                print(f"处理入库单失败: {item['stockinNo']} - {str(e)}")
                error_count += 1
                continue
        
        print(f"本批次处理完成: 成功={success_count}, 失败={error_count}, 跳过={skipped_count}")
        return success_count, error_count
        
    except Exception as e:
        print(f"更新入库单数据失败: {str(e)}")
        raise

def sync_all_stock():
    """同步所有库存数据"""
    try:
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        
        page = 1
        total_success = 0
        total_error = 0
        
        while True:
            # 获取当前页数据
            stockin_data = sync_stockin_data(start_date, end_date, page)
            
            # 更新到数据库
            success_count, error_count = update_stockin_data(stockin_data)
            total_success += success_count
            total_error += error_count
            
            # 检查是否还有下一页
            if page >= stockin_data['max_page']:
                break
            
            # 继续下一页
            page += 1
            time.sleep(10)  # 避免请求过快
        
        return True, f"入库单同步完成，成功: {total_success} 条，失败: {total_error} 条"
        
    except Exception as e:
        return False, f"同步入库单时发生错误: {str(e)}"
```

然后再处理出库数据，请参考API文档链接：https://zsxj.yuque.com/cdy1c2/ie96h9/fy76x4#QxdJZ；

每一条入库记录，都通过业务单号，查询到对应的出库单，保存到出库记录中，这样我们后续分析订单数据的时候，就可以通过关联关系，清楚的知道订单的出库成本。



#### 销售管理

##### 基础功能

销售主要目前主要通过Shopify平台来销售，但目前不需要对接Shopify，而是通过旺店通来获取订单数据。

但同时还存在线下的订单，所以需要有手动录入的功能。

需要注意的是，订单是跟包裹关联的，但此时我们还未在logistics应用中创建package模型。

我们先来创建模型，主要是店铺、订单、订单明细，以及其他必要的模型。

请帮我创建相应的模型，主要是供应商、采购主单、采购明细，以及其他必要的模型。

请参考以下我创建过的模型文件:	

```python
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

class Shop(models.Model):
    PLATFORM_CHOICES = (
        ('SHOPIFY', 'Shopify'),
        ('AMAZON', 'Amazon'),
        ('EBAY', 'eBay'),
        ('WALMART', 'Walmart'),
        ('OTHER', '其他'),
    )

    id = models.AutoField('ID', primary_key=True)
    name = models.CharField('店铺名称', max_length=100)
    code = models.CharField('店铺编码', max_length=50, unique=True)
    platform = models.CharField('平台', max_length=20, choices=PLATFORM_CHOICES)
    is_active = models.BooleanField('启用状态', default=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '店铺'
        verbose_name_plural = '店铺'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_platform_display()})"

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'pending', _('待处理')
        PROCESSING = 'processing', _('处理中')
        SHIPPED = 'shipped', _('已发货')
        COMPLETED = 'completed', _('已完成')
        CANCELLED = 'cancelled', _('已取消')
    
    class OrderType(models.TextChoices):
        PLATFORM = 'platform', _('平台订单')
        INFLUENCER = 'influencer', _('达人订单')
        OFFLINE = 'offline', _('线下订单')
        REQUISITION = 'requisition', _('员工领用')
        EMPLOYEE = 'employee', _('员工自购')
        
    
    order_no = models.CharField(max_length=64, unique=True)
    platform_order_no = models.CharField(max_length=64, blank=True, default='')
    shop = models.ForeignKey('Shop', on_delete=models.CASCADE)
    sales_rep = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='销售员',
        related_name='sales_orders'
    )
    order_type = models.CharField(
        '订单类型',
        max_length=20,
        choices=OrderType.choices,
        default=OrderType.PLATFORM,
        help_text='订单来源类型'
    )
    status = models.CharField(
        max_length=32,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING
    )
    recipient_country = models.CharField(max_length=64)
    recipient_state = models.CharField(max_length=64)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField(auto_now=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    freight = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    recipient_name = models.CharField(max_length=100)
    recipient_phone = models.CharField(max_length=20)
    recipient_email = models.EmailField(blank=True, default='')
    recipient_city = models.CharField(max_length=50)
    recipient_address = models.CharField(max_length=100)
    recipient_postcode = models.CharField('邮编', max_length=20, blank=True, default='')
    system_remark = models.TextField('系统备注', blank=True, default='')
    cs_remark = models.TextField('客服备注', blank=True, default='')
    buyer_remark = models.TextField('买家备注', blank=True, default='')

    class Meta:
        verbose_name = '订单'
        verbose_name_plural = '订单'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_no}"

    def get_sku_stats(self):
        """获取SKU统计信息"""
        sku_count = self.cart_set.count()  # SKU种类数
        total_qty = sum(cart.qty for cart in self.cart_set.all())  # SKU总数量
        return {
            'sku_count': sku_count,
            'total_qty': total_qty
        }

class Cart(models.Model):
    id = models.AutoField('ID', primary_key=True)
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='订单'
    )
    sku = models.ForeignKey(
        'gallery.SKU',
        on_delete=models.PROTECT,
        verbose_name='SKU'
    )
    qty = models.IntegerField(
        '数量',
        default=1
    )
    price = models.DecimalField(
        '售价',
        max_digits=10,
        decimal_places=2
    )
    cost = models.DecimalField(
        '成本',
        max_digits=10,
        decimal_places=2
    )
    discount = models.DecimalField(
        '折扣',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    actual_price = models.DecimalField(
        '实际售价',
        max_digits=10,
        decimal_places=2
    )
    is_out_of_stock = models.BooleanField(
        '缺货状态',
        default=False
    )
    created_at = models.DateTimeField(
        '创建时间',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        '更新时间',
        auto_now=True
    )

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = '购物车'
        ordering = ['-created_at']

    def __str__(self):
        return f"订单 {self.order.order_no} - {self.sku.sku_code}"

```

以及订单数据的API接口文档：https://zsxj.yuque.com/cdy1c2/ie96h9/xtvmyr

模型创建之后，再创建相应的列表，增删改查功能。并实现左侧菜单入口。

订单的列表，我希望以页签的形式来展示，不同的页面可以看到不同状态的订单列表。

注意给列表加上分页的功能。

##### 订单新增功能

​	请仔细阅读\templates\trade\order_form.html，这是我初步设计的一个新增订单的页面。请参考这个页面设计订单行政的功能：

​	1，订单基础信息的填写，其中订单号在用户选定订单类型后自动填充。店铺默认为shopID为1的店铺，手工填写的订单都会归属于这个店铺。

​	2，用户的地址，除了可以通过输入框输入之外，帮我增加一个自动识别的功能，用户可以点击按钮弹窗一个文本输入框，用户可以在输入框中粘贴含有各项信息的文本，点击自动识别后，会自动提取各个字段的信息，并填充到相应的输入框中，可以参考一下下面这个截图：

<img src="C:\Users\75781\Documents\WeChat Files\wxid_91uzfifdmdvp91\FileStorage\Temp\51fe9a452800a4193658f4225c47249.jpg" alt="51fe9a452800a4193658f4225c47249" style="zoom:50%;" />

这是顺丰快递小程序的地址信息输入框，可以参考这个图片来实现我需要的自动识别填写地址的功能。

​	3，商品信息的录入，通过输入框输入搜索SKU编码来选择具体的商品，并展示选中SKU的信息。SKU的销售单价默认为空，且必填。

​	4，用户支付的运费，输入框中默认值为0，支持修改。

​	5，仓配相关信息，默认选择 ID=8的仓库，默认选择ID=1的service，都可以支持修改。但是提交定的时候，会校验仓库的商品库存是否充足，如果不充足，则弹窗提醒用户，如果用户确认，依然可以正常下单。

​	除了仓库和物流服务，仓配信息中还需要有包裹中的商品明细，这个与SKU明细对应，主要是中英文品名，但支持手动修改。

​	订单成功创建后，会自动创建包裹，仓配信息将作为package的字段内容保存报package模型中。

需要注意：

​	1，订单的支付金额=商品金额+用户支付运费。

​	2，包裹的创建，可以考虑使用异步模式，这样提高交互的相应。



##### 数据同步

订单数据，也需要从旺店通ERP系统拉取，请仔细阅读API文档https://zsxj.yuque.com/cdy1c2/ie96h9/xtvmyr。

同时参考我历史写的同步代码：	

```python
import time
import hashlib
import json
import math
import requests
import logging
from datetime import datetime, timedelta
from django.utils import timezone
from .models import Order, Shop, Cart
from gallery.models import SKU  # 避免循环导入
from logistics.models import Package, Service  # 添加Package导入
from storage.models import Warehouse  # 添加Warehouse导入

# 获取logger实例
logger = logging.getLogger(__name__)

def generate_sign(body):
    """生成API签名"""
    appName = "mathmagic"
    appKey = "82be0592545283da00744b489f758f99"
    sid = "mathmagic"

    headers = {
        'Content-Type': 'application/json'
    }

    timestamp = str(int(time.time()))
    sign_str = "{appKey}appName{appName}body{body}sid{sid}timestamp{timestamp}{appKey}".format(
        appKey=appKey, appName=appName, body=body, sid=sid, timestamp=timestamp
    )
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    
    params = {
        "appName": appName,
        "sid": sid,
        "sign": sign,
        "timestamp": timestamp,
    }
    return params, headers

def get_trade_detail(trade_id):
    """获取订单明细数据"""
    body = {
        "tradeIds": [str(trade_id)]
    }
    body_str = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    params, headers = generate_sign(body_str)
    
    url = "https://openapi.qizhishangke.com/api/openservices/trade/v1/getSalesTradeOrderList"
    response = requests.post(url, params=params, headers=headers, data=body_str)

    # 打印返回的数据结构
    # print("API返回数据:", response.json()['data'] )


    if response.status_code != 200:
        raise Exception(f"API请求失败: {response.text}")
        
    response_data = response.json()
    if response_data['code'] != 200:
        raise Exception(f"API返回错误: {response_data['message']}")
    

    
    return response_data['data']

def sync_trade_detail(order, trade_id):
    """同步订单商品明细"""
    try:
        # 获取订单明细数据
        details = get_trade_detail(trade_id)
        
        # 删除原有的购物车记录
        Cart.objects.filter(order=order).delete()
        
        # 同步商品明细
        for item in details:
            try:
                # 使用正确的字段名获取SKU编码
                sku_code = item.get('skuNo')
                if not sku_code:
                    logger.error(f"找不到SKU编码字段, 订单号: {order.order_no}, 数据: {item}")
                    continue
                    
                sku = SKU.objects.get(sku_code=sku_code)
                
                # 创建购物车记录
                Cart.objects.create(
                    order=order,
                    sku=sku,
                    qty=int(item.get('num', 1)),
                    price=float(item.get('price', 0)),
                    cost=float(item.get('cost', 0)),
                    discount=float(item.get('discount', 0)),
                    actual_price=float(item.get('actualPrice', item.get('price', 0))),
                    is_out_of_stock=False
                )
            except SKU.DoesNotExist:
                logger.error(f"找不到SKU: {sku_code}, 订单号: {order.order_no}")
                continue
            except Exception as e:
                logger.error(f"处理订单商品明细时出错: {str(e)}, 订单号: {order.order_no}")
                continue
                
    except Exception as e:
        logger.error(f"获取订单明细数据失败: {str(e)}, 订单号: {order.order_no}")

def sync_package_info(order, trade_data):
    """同步包裹信息"""
    logger.info(f"开始同步包裹信息, 订单号: {order.order_no}")
    logger.info(f"物流数据: {json.dumps(trade_data, ensure_ascii=False)}")
    
    try:
        # 检查订单状态
        status_desc = trade_data.get('tradeStatusDesc')
        logger.info(f"订单状态: {status_desc}")
        
        # 如果订单已取消或递交中，跳过包裹同步
        if status_desc in ['已取消', '递交中']:
            logger.info(f"订单 {order.order_no} 状态为{status_desc}，跳过包裹同步")
            return
            
        logger.info(f"物流单号: {trade_data.get('logisticsNo')}")
        logger.info(f"物流公司代码: {trade_data.get('logisticsCompanyCode')}")
        
        # 获取物流服务，使用ID为1的默认服务
        try:
            service = Service.objects.get(id=1)
            logger.info(f"使用默认物流服务: {service}")
        except Service.DoesNotExist:
            logger.error("找不到默认物流服务(ID=1)")
            return
        except Exception as e:
            logger.error(f"获取物流服务时出错: {str(e)}")
            return

        # 获取仓库信息
        warehouse_id = trade_data.get('warehouseNo')
        if not warehouse_id:
            logger.info(f"订单 {order.order_no} 未指定仓库，使用默认仓库(ID=1)")
            warehouse_id = '1'  # 使用默认仓库
            
        try:
            warehouse = Warehouse.objects.get(id=warehouse_id)
            logger.info(f"找到仓库: {warehouse.name} (ID: {warehouse.id})")
        except Warehouse.DoesNotExist:
            logger.error(f"找不到仓库ID为 {warehouse_id} 的仓库，使用默认仓库(ID=1)")
            try:
                warehouse = Warehouse.objects.get(id=1)
            except Warehouse.DoesNotExist:
                logger.error("找不到默认仓库(ID=1)")
                return
        except Exception as e:
            logger.error(f"获取仓库信息时出错: {str(e)}")
            return

        # 创建或更新包裹记录
        try:
            package_data = {
                'order': order,
                'warehouse': warehouse,  # 添加仓库信息
                'tracking_no': trade_data.get('logisticsNo', ''),  # 未发货时可能没有物流单号
                'pkg_status_code': '1' if status_desc == '已发货' else '0',
                'service': service,
                'items': [],  # 商品信息暂时为空列表
                'shipping_fee': float(trade_data.get('postFee', 0))
            }
            logger.info(f"准备创建/更新包裹记录: {json.dumps(package_data, ensure_ascii=False, default=str)}")
            
            # 尝试获取现有包裹
            try:
                package = Package.objects.get(order=order)
                # 更新现有包裹
                for key, value in package_data.items():
                    setattr(package, key, value)
                package.save()
                logger.info(f"更新包裹记录成功: {package.tracking_no or '未获取跟踪号'}, 订单号: {order.order_no}")
            except Package.DoesNotExist:
                # 创建新包裹
                package = Package.objects.create(**package_data)
                logger.info(f"创建新包裹记录成功: {package.tracking_no or '未获取跟踪号'}, 订单号: {order.order_no}")
                
        except Exception as e:
            logger.error(f"创建/更新包裹记录时出错: {str(e)}")
            logger.error("错误详情: ", exc_info=True)
            return
            
    except Exception as e:
        logger.error(f"同步包裹信息失败: {str(e)}, 订单号: {order.order_no}")
        logger.error("错误详情: ", exc_info=True)

def sync_trade_data(start_date, end_date, page=1):
    """同步订单数据"""
    body = {
        "createTimeBegin": start_date,
        "createTimeEnd": end_date,
        "tradeStatusCode": 0,
        "pageNo": page,
        "pageSize": 100
    }
    body_str = json.dumps(body, ensure_ascii=False, separators=(",", ":"))
    params, headers = generate_sign(body_str)
    
    url = "https://openapi.qizhishangke.com/api/openservices/trade/v1/getSalesTradeList"
    response = requests.post(url, params=params, headers=headers, data=body_str)
    
    if response.status_code != 200:
        raise Exception(f"API请求失败: {response.text}")
        
    response_data = response.json()
    if response_data['code'] != 200:
        raise Exception(f"API返回错误: {response_data['message']}")
        
    data = response_data['data']
    
    for item in data['data']:
        # 处理时间字段
        created_time = datetime.strptime(item['tradeTime'], "%Y-%m-%dT%H:%M:%S")
        try:
            shiped_time = datetime.strptime(item['deliveryTime'], "%Y-%m-%dT%H:%M:%S")
            shiped_date = shiped_time.date()
        except:
            shiped_time = None
            shiped_date = None
            
        try:
            operate_time = datetime.strptime(item['outBoundTime'], "%Y-%m-%dT%H:%M:%S")
        except:
            operate_time = None

        # 获取或创建Shop
        shop, _ = Shop.objects.get_or_create(
            code=item['shopNo'],
            defaults={
                'name': item['shopText'],
                'is_active': True
            }
        )

        # 状态映射
        status_mapping = {
            '待发货': Order.OrderStatus.PENDING,
            '已发货': Order.OrderStatus.SHIPPED,
            '已完成': Order.OrderStatus.COMPLETED,
            '已取消': Order.OrderStatus.CANCELLED,
            # 添加其他状态映射...
        }

        # 更新或创建Order
        order_data = {
            'platform_order_no': item['srcTids'],
            'order_no': item['tradeNo'],
            'recipient_country': item['country'],
            'recipient_state': item['receiverProvince'],
            'created_at': created_time,
            'shop': shop,
            'status': status_mapping.get(item['tradeStatusDesc'], Order.OrderStatus.PENDING),
            'paid_amount': float(item.get('payment', 0)),
            'freight': float(item.get('postFee', 0)),
            'recipient_name': item['receiverName'],
            'recipient_phone': item['receiverMobile'],
            'recipient_email': '',
            'recipient_city': item['receiverCity'],
            'recipient_address': item['receiverAddress'],
            'system_remark': item['erpRemark'],
            'cs_remark': item['csRemark'],
            'buyer_remark': item['buyerMessage']
        }

        try:
            # 创建或更新订单
            order, created = Order.objects.update_or_create(
                id=item['tradeId'],
                defaults=order_data
            )
            print('处理订单', item['srcTids'], '成功============================================================')
            
            # 同步订单商品明细
            sync_trade_detail(order, item['tradeId'])
            
            # 同步包裹信息
            sync_package_info(order, item)
            
        except Exception as e:
            logger.error(f"处理订单 {item['srcTids']} 时出错: {str(e)}")
            continue
    
    # 处理分页
    if page < math.ceil(data['total'] / data['pageSize']):
        sync_trade_data(start_date, end_date, page + 1)

def sync_all_trade():
    """同步所有订单数据"""
    try:
        # 设置同步的时间范围（比如最近7天的订单）
        end_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
        
        # 开始同步数据
        sync_trade_data(start_date, end_date)
        
        return True, "订单数据同步成功"
    except Exception as e:
        logger.error(f"同步订单数据时出错: {str(e)}")
        return False, f"同步失败: {str(e)}" 
```

帮我实现数据同步功能，

​	1，通过API 获取订单列表

​	2，提取订单信息，根据订单号判断是否已经已经存在于当前数据库，如果不存在则新增，存在则更新订单数据。

​	3，同步创建包裹记录，更新包裹的状态。

请在订单列表页面，帮我增加一个按钮，通过点击按钮会触发同步。

#### 物流管理

​	物流商是物流服务提供者，每一个物流商会提供多种Service，每一种Service对应不同的价格和时效。

​	包裹基于订单数据创建，包裹跟订单是一对一的关系。包裹创建之后，需要通过API接口将包裹数据推送给到服务商，并从服务商接口获取返回的物流单号，同样从API接口获取更新的物流轨迹状态。

​	现在，让我先来创建模型，主要是物流商、物流服务、包裹；轨迹、物流价格和时效的功能我们暂时不开发。请参考我历史创建的模型代码，帮我新建模型：	

```python
from django.db import models
from trade.models import Order


class Carrier(models.Model):
    """物流商模型"""
    id = models.AutoField('ID', primary_key=True)
    name_zh = models.CharField('中文名称', max_length=25)
    name_en = models.CharField('英文名称', max_length=25)
    code = models.CharField('物流商代码', max_length=10, unique=True)
    url = models.URLField('官网地址', blank=True)
    contact = models.CharField('联系电话', max_length=20, blank=True)
    key = models.IntegerField('查询代码', null=True, blank=True)
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '物流商'
        verbose_name_plural = '物流商'
        ordering = ['name_zh']
        db_table = 'logistics_carrier'

    def __str__(self):
        return f"{self.name_zh} ({self.name_en})"


class Service(models.Model):
    """物流服务模型"""
    id = models.AutoField('ID', primary_key=True)
    carrier = models.ForeignKey(
        Carrier,
        on_delete=models.CASCADE,
        verbose_name='物流商'
    )
    service_name = models.CharField('服务名称', max_length=25)
    service_code = models.CharField('服务代码', max_length=10)
    service_type = models.IntegerField('服务类型')
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '物流服务'
        verbose_name_plural = '物流服务'
        ordering = ['carrier', 'service_name']
        db_table = 'logistics_service'
        unique_together = ['carrier', 'service_code']  # 确保同一物流商下服务代码唯一

    def __str__(self):
        return f"{self.carrier.name_zh} - {self.service_name}"


class Package(models.Model):
    """包裹模型"""
    id = models.AutoField('ID', primary_key=True)
    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        verbose_name='订单',
        related_name='package'
    )
    warehouse = models.ForeignKey(
        'storage.Warehouse',
        on_delete=models.PROTECT,
        verbose_name='发货仓库',
        null=True,
        blank=True
    )
    tracking_no = models.CharField(
        '跟踪号',
        max_length=30,
        blank=True,
        null=True
    )
    pkg_status_code = models.CharField(
        '包裹状态码',
        max_length=4,
        default='0'
    )
    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,  # 使用PROTECT避免误删除物流服务
        verbose_name='物流服务'
    )
    items = models.JSONField(
        '商品列表',
        help_text='包含SKU、品名、包裹尺寸、重量等信息'
    )
    shipping_fee = models.DecimalField(
        '运费',
        max_digits=10,
        decimal_places=2,
        default=0
    )
    created_at = models.DateTimeField('创建时间', auto_now_add=True)
    updated_at = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        verbose_name = '包裹'
        verbose_name_plural = '包裹'
        ordering = ['-created_at']
        db_table = 'logistics_package'

    def __str__(self):
        return f"包裹 {self.id} - {self.tracking_no or '未获取跟踪号'}"

    @property
    def carrier_name(self):
        """获取物流商名称"""
        return self.service.carrier.name_zh if self.service else ''

    @property
    def service_name(self):
        """获取服务名称"""
        return self.service.service_name if self.service else ''

```

​	模型创建之后，请帮我创建相应的列表视图，添加增删改查功能，并在左侧的菜单栏添加相应的入口。

#### 页面管理

​	我希望将一些夸应用的信息展示，同意放到这个应用中，方便路由和模板的管理。

​	首先先帮我创建一个主页，请参考templates\home_page.html 把重要的汇总数据，放到这个页面上。方便查看。

#### 生产管理

​	生产管理功能涵盖生产订单发起，处理，数据分析，实现对人员、工厂的筛选评估，生产流程的全称管控。

​	具体功能如下：

​	1，用户可以新建生产订单，生产订单包含样品订单和量产订单。

​	2，管理员可以对订单进行管理，指定跟单人员。

​	3，跟单人员可以修改订单的承接工厂，修改订单的状态，预计的完成、交货时间。

​	4，展示订单目前的状态。

​	5，对于样品订单，会单独创建一个打样详情记录，类似博客的方式，用户可以把评审记录记录下来。

​	生产管理没有历史的代码，也不需要从API获取信息，请帮我设计相关功能并实现它。

​	



​	

#### 

