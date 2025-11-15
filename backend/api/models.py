from django.db import models
import os
from django.conf import settings

class Script(models.Model):
    """
    自动化脚本模型
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="脚本名称")
    description = models.TextField(blank=True, null=True, verbose_name="脚本描述")
    content = models.JSONField(verbose_name="脚本内容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    def __str__(self):
        return self.name

class Task(models.Model):
    """
    自动化任务模型
    """
    STATUS_CHOICES = [
        ('PENDING', '待处理'),
        ('RUNNING', '运行中'),
        ('SUCCESS', '成功'),
        ('FAILED', '失败'),
        ('PAUSED', '已暂停'),
    ]

    script = models.ForeignKey(Script, on_delete=models.CASCADE, verbose_name="关联脚本")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name="任务状态")
    log = models.TextField(blank=True, null=True, verbose_name="任务日志")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    started_at = models.DateTimeField(null=True, blank=True, verbose_name="开始时间")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="完成时间")
    # 用于存储截图的相对路径或ID，方便后续查询
    latest_screenshot = models.CharField(max_length=255, null=True, blank=True, verbose_name="最新截图")

    @property
    def latest_screenshot_url(self):
        if self.latest_screenshot:
            url_path = str(self.latest_screenshot).replace(os.path.sep, '/')
            return f"{settings.MEDIA_URL}{url_path}"
        return None

    def __str__(self):
        return f"任务 #{self.id} - {self.script.name} ({self.get_status_display()})"
