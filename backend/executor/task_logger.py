from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from api.models import Task  # 从 api 应用导入 Task 模型
from api.serializers import TaskSerializer # 从 api 应用导入 Task 序列化器

class TaskLogger:
    """
    一个专门用于处理任务日志记录、状态更新和WebSocket广播的类。
    """
    def __init__(self, task_id):
        try:
            # 初始加载一次任务，主要为了获取ID
            self.task = Task.objects.get(id=task_id)
            self.task_id = task_id
            self.channel_layer = get_channel_layer()
        except Task.DoesNotExist:
            raise ValueError(f"Task with ID {task_id} does not exist.")

    def log(self, message, status=None):
        try:
            current_task = Task.objects.get(id=self.task_id)

            log_message = f"{message}\n"
            current_task.log = (current_task.log or '') + log_message

            if status:
                current_task.status = status

            if status in ['SUCCESS', 'FAILED']:
                current_task.completed_at = timezone.now()

            # 保存包含了所有最新信息（包括其他任务可能写入的截图路径）的对象
            current_task.save()

            # 使用最新的对象进行序列化和广播
            self.broadcast(current_task)

        except Task.DoesNotExist:
            pass

    def update_screenshot(self, screenshot_path):
        # 这个方法现在也可以从这个修复中受益
        try:
            current_task = Task.objects.get(id=self.task_id)
            current_task.latest_screenshot = screenshot_path
            current_task.save()
            self.broadcast(current_task)
        except Task.DoesNotExist:
            pass

    def broadcast(self, task_instance):
        serializer = TaskSerializer(task_instance)
        async_to_sync(self.channel_layer.group_send)(
            'task_updates',
            {
                'type': 'task.update',
                'message': serializer.data
            }
        )