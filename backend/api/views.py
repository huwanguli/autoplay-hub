from rest_framework import viewsets, status,permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Script, Task
from .serializers import ScriptSerializer, TaskSerializer
from executor.tasks import execute_automation_task, take_manual_screenshot_task
import subprocess
import re
from rest_framework.decorators import api_view
from django.utils import timezone
from executor.task_logger import TaskLogger
from backend.celery import app as celery_app


class ScriptViewSet(viewsets.ModelViewSet):
    serializer_class = ScriptSerializer
    # ★ 1. 设置权限: 对于读操作(GET)允许任何人,对于写操作(POST,PUT,DELETE)必须登录
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        ★ 2. 重写此方法，实现数据隔离
        """
        user = self.request.user
        if user.is_authenticated:
            # 如果用户已登录，只返回属于该用户的脚本
            return Script.objects.filter(owner=user).order_by('-created_at')

        # 如果用户未登录，不返回任何数据库中的脚本
        return Script.objects.none()

    def perform_create(self, serializer):
        """
        ★ 3. 创建脚本时，自动将当前登录用户设置为所有者
        """
        # permission_classes确保了只有登录用户才能调用create
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        script = self.get_object()
        device_uri = request.data.get('device_uri')
        if not device_uri:
            return Response({'error': "'device_uri' 字段是必需的"}, status=status.HTTP_400_BAD_REQUEST)

        # ★ 4. 在创建Task时，也记录下任务的所有者
        owner = request.user if request.user.is_authenticated else None

        new_task = Task.objects.create(
            script=script,
            status='PENDING',
            device_uri=device_uri,
            owner=owner
        )

        task_result = execute_automation_task.delay(new_task.id, device_uri)
        new_task.celery_task_id = task_result.id
        new_task.save()

        print(f"创建任务 #{new_task.id}，Celery ID: {task_result.id}")
        serializer = TaskSerializer(new_task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    # ★ 5. 同样为Task视图集设置权限和数据隔离
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    http_method_names = ['get', 'head', 'options']
    pagination_class = None

    def get_queryset(self):
        """为Task实现数据隔离"""
        user = self.request.user
        if user.is_authenticated:
            return Task.objects.filter(owner=user).order_by('-created_at')
        return Task.objects.none()



# ... (list_devices 和 manual_screenshot 函数保持不变) ...
@api_view(['GET'])
def list_devices(request):
    try:
        result = subprocess.run(['adb', 'devices', '-l'], capture_output=True, text=True, check=True, encoding='utf-8')
        devices = []
        lines = result.stdout.strip().split('\n')[1:]
        for line in lines:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[1] == 'device':
                uri = f"Android:///{parts[0]}"
                model_match = re.search(r'model:(\S+)', line)
                model = model_match.group(1) if model_match else 'Unknown'
                devices.append({'uri': uri, 'serial': parts[0], 'status': parts[1], 'model': model})
        return Response(devices)
    except FileNotFoundError:
        return Response({'error': "未找到 'adb' 命令。"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': f"发生未知错误: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def manual_screenshot(request, pk):
    try:
        task = Task.objects.get(pk=pk)
        if task.status not in ['RUNNING', 'PENDING']:
            return Response({'error': '任务已结束，无法截图'}, status=status.HTTP_400_BAD_REQUEST)
        take_manual_screenshot_task.delay(task.id)
        return Response({'status': '截图指令已发送'})
    except Task.DoesNotExist:
        return Response({'error': '任务不存在'}, status=status.HTTP_404_NOT_FOUND)


# ↓↓↓ 这是我们修正后的 cancel_task 视图 ↓↓↓
@api_view(['POST'])
def cancel_task(request, pk):
    """
    取消一个正在运行或等待中的任务。pk是数据库Task的ID。
    """
    try:
        task = Task.objects.get(pk=pk)
        if not task.celery_task_id:
            return Response({'error': '任务没有关联的Celery ID，无法取消'}, status=status.HTTP_400_BAD_REQUEST)

        if task.status not in ['PENDING', 'RUNNING']:
            return Response({'error': f'任务状态为 {task.status}，无法取消'}, status=status.HTTP_400_BAD_REQUEST)

        # 我们用这个实例来发送 revoke 指令
        celery_app.control.revoke(task.celery_task_id, terminate=True, signal='SIGKILL')
        # 立即更新数据库状态为CANCELED
        task.status = 'CANCELED'
        task.completed_at = timezone.now()
        task.log = (task.log or '') + "\n--- [任务已被用户手动取消] ---"
        task.save()
        # 通过WebSocket广播最终状态
        logger = TaskLogger(task.id)
        logger.broadcast(task)
        return Response({'status': '取消指令已发送'})

    except Task.DoesNotExist:
        return Response({'error': '任务不存在'}, status=status.HTTP_404_NOT_FOUND)