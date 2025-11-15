from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Script, Task
from .serializers import ScriptSerializer, TaskSerializer
# 1. 从 .tasks 文件导入我们刚刚创建的Celery任务函数
from .tasks import execute_automation_task


class ScriptViewSet(viewsets.ModelViewSet):
    """
    用于查看和编辑脚本的API视图。
    (这部分保持不变)
    """
    queryset = Script.objects.all().order_by('-created_at')
    serializer_class = ScriptSerializer

    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """
        一个自定义的API端点，用于直接运行一个脚本。
        它会自动创建一个新任务并执行。
        URL: /api/scripts/{id}/run/
        """
        script = self.get_object()  # 获取当前脚本实例
        if not isinstance(script.content, dict):
            return Response(
                {'error': f"脚本内容格式错误，必须是一个JSON对象，而不是字符串。请检查脚本 #{script.id}。"},
                status=status.HTTP_400_BAD_REQUEST
            )
        # 1. 创建一个新的Task实例，并关联到这个脚本
        new_task = Task.objects.create(script=script, status='PENDING')

        # 2. 将这个新任务的ID发送到Celery队列
        execute_automation_task.delay(new_task.id)

        print(f"基于脚本 '{script.name}' 创建并运行了新任务 #{new_task.id}")

        # 3. 返回新创建的任务信息，方便前端跳转查看
        serializer = TaskSerializer(new_task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskViewSet(viewsets.ModelViewSet):
    """
    用于查看和创建任务的API视图。
    """
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    # 限制API只允许 'get' (获取列表/详情) 和 'post' (创建)
    http_method_names = ['get', 'post', 'head', 'options']

    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """
        一个自定义的API端点，用于启动任务。
        URL: /api/tasks/{id}/run/
        """
        task = self.get_object()

        # 检查任务是否是“待处理”状态，防止重复启动
        if task.status != 'PENDING':
            return Response(
                {'error': '任务正在运行或已完成，无法重复启动'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 2. **核心改动**: 使用 .delay() 将任务发送到Celery队列
        #    这个调用会立即返回，不会阻塞API响应。
        #    我们将任务的数据库ID作为参数传给后台任务。
        execute_automation_task.delay(task.id)

        # 在服务器控制台打印日志，方便调试
        print(f"任务 {task.id} 已成功加入后台执行队列。")

        # 3. 立即向用户返回成功的响应
        return Response({
            'status': 'success',
            'message': f'任务 {task.id} 已成功加入后台执行队列，稍后将开始运行。'
        })