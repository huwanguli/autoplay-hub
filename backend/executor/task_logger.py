from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from api.models import Task  # 从 api 应用导入 Task 模型
from api.serializers import TaskSerializer # 从 api 应用导入 Task 序列化器

class TaskLogger:
    """
    一个专门用于处理任务日志记录、状态更新和WebSocket广播的类。
    """
    def __init__(self, task_id: int):
        self.task_id = task_id
        self.task = Task.objects.get(id=task_id)
        self.log_content = self.task.log or ""  # 从数据库加载现有日志
        self.channel_layer = get_channel_layer()

    def log(self, message: str, status: str = None):
        """记录一条新日志，并选择性地更新状态，然后广播。"""
        print(f"[Task #{self.task_id}] {message}") # 在Celery控制台打印
        self.log_content += message + "\n"
        self.task.log = self.log_content

        if status:
            self.task.status = status
            if status in ['SUCCESS', 'FAILED']:
                self.task.completed_at = timezone.now()

        # 保存所有变更到数据库
        self.task.save()
        self._broadcast()

    def update_screenshot(self, screenshot_path: str):
        """专门用于更新截图并广播的方法。"""
        self.task.latest_screenshot = screenshot_path
        self.task.save()
        self.log(f"截图已更新: {screenshot_path}") # 同时也记录一条日志

    def _broadcast(self):
        """私有方法，用于通过WebSocket广播当前任务的完整状态。"""
        serializer = TaskSerializer(self.task)
        async_to_sync(self.channel_layer.group_send)(
            'task_updates',
            {
                'type': 'task.update',
                'message': serializer.data
            }
        )