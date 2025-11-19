import pymysql
#使用pymysql替代默认的MySQLdb
pymysql.install_as_MySQLdb()
# 确保Celery app在Django启动时被加载，这样@shared_task才能正常工作
from .celery import app as celery_app
__all__ = ('celery_app',)