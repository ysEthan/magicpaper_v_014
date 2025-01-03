# 物流API配置
LOGISTICS_API_BASE = 'https://api.logistics-provider.com/v1'
LOGISTICS_API_KEY = 'your-api-key'

# Celery配置
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Celery定时任务
CELERY_BEAT_SCHEDULE = {
    'update_tracking_info': {
        'task': 'logistics.tasks.update_tracking_info',
        'schedule': 3600.0,  # 每小时执行一次
    },
} 