import os
from celery import Celery

# 为celery程序设置django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 创建Celery应用实例
app = Celery('backend')

# Celery将使用'CELERY_'前缀的变量作为配置
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动从所有已注册的Django app中加载tasks.py文件
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')