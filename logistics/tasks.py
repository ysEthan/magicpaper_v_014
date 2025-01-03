import requests
from django.utils import timezone
from django.conf import settings
from .models import Package

def update_tracking_info():
    """更新物流跟踪信息"""
    # 获取需要更新的包裹
    packages = Package.objects.filter(
        status__in=['shipped'],  # 只更新已发货的包裹
        tracking_no__isnull=False  # 必须有跟踪号
    ).exclude(
        service__carrier__tracking_url=''  # 必须有跟踪链接
    )
    
    for package in packages:
        try:
            # 调用物流API获取跟踪信息
            carrier = package.service.carrier
            api_url = f"{settings.LOGISTICS_API_BASE}/tracking"
            
            response = requests.get(api_url, params={
                'carrier': carrier.code,
                'tracking_no': package.tracking_no
            }, headers={
                'Authorization': f'Bearer {settings.LOGISTICS_API_KEY}'
            })
            
            if response.status_code == 200:
                data = response.json()
                
                # 更新包裹跟踪信息
                package.tracking_info = data.get('tracking_info', [])
                
                # 根据最新的跟踪状态更新包裹状态
                latest_status = data.get('status')
                if latest_status == 'delivered':
                    package.status = Package.PackageStatus.DELIVERED
                    package.delivered_at = timezone.now()
                elif latest_status == 'returned':
                    package.status = Package.PackageStatus.RETURNED
                elif latest_status == 'lost':
                    package.status = Package.PackageStatus.LOST
                
                package.save()
                
        except Exception as e:
            print(f"更新包裹 {package.id} 的跟踪信息失败: {str(e)}")
            continue 