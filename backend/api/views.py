from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Script, Task
from .serializers import ScriptSerializer, TaskSerializer
from executor.tasks import execute_automation_task, take_manual_screenshot_task
import subprocess
import re
from rest_framework.decorators import api_view


class ScriptViewSet(viewsets.ModelViewSet):
    """
    用于查看、创建和运行脚本的API视图。
    """
    queryset = Script.objects.all().order_by('-created_at')
    serializer_class = ScriptSerializer

    @action(detail=True, methods=['post'])
    def run(self, request, pk=None):
        """
        一个自定义的API端点，用于直接运行一个脚本。
        URL: /api/scripts/{id}/run/
        现在需要一个包含 'device_uri' 的POST请求体。
        """
        script = self.get_object()

        # ★ 关键改动 1：从请求体中获取 device_uri
        device_uri = request.data.get('device_uri')
        if not device_uri:
            return Response({'error': "'device_uri' 字段是必需的"}, status=status.HTTP_400_BAD_REQUEST)

        # 检查脚本内容格式
        if not isinstance(script.content, dict):
            return Response(
                {'error': f"脚本内容格式错误，必须是一个JSON对象。请检查脚本 #{script.id}。"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 创建一个新的Task实例
        new_task = Task.objects.create(script=script, status='PENDING',device_uri=device_uri)

        # ★ 关键改动 2：将 new_task.id 和 device_uri 一起传递给 Celery
        execute_automation_task.delay(new_task.id, device_uri)

        print(f"基于脚本 '{script.name}' 创建并运行了新任务 #{new_task.id}")

        # 返回新创建的任务信息
        serializer = TaskSerializer(new_task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskViewSet(viewsets.ModelViewSet):
    """
    用于查看和管理任务的API视图。
    """
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer
    http_method_names = ['get', 'head', 'options']  # ★ 我们暂时移除 'post' 和 'run'，让任务只能由运行脚本来创建

    pagination_class = None

@api_view(['GET'])
def list_devices(request):
    """
    运行 'adb devices -l' 命令，解析并返回一个设备列表。
    """
    try:
        # 运行 adb devices -l 命令。-l 参数可以提供更详细的信息，如设备型号。
        # 'universal_newlines=True' (或 'text=True') 让输出是文本而不是字节
        result = subprocess.run(
            ['adb', 'devices', '-l'],
            capture_output=True,
            text=True,
            check=True,  # 如果命令返回非零退出码，则会引发CalledProcessError
            encoding='utf-8'
        )

        devices = []
        # adb devices 的输出通常以 "List of devices attached" 开头，我们跳过这一行
        lines = result.stdout.strip().split('\n')[1:]

        for line in lines:
            if not line.strip():
                continue

            # 使用正则表达式解析每一行，例如:
            # "emulator-5554          device product:sdk_gphone64_x86_64 model:sdk_gphone64_x86_64 device:generic_x86_64 transport_id:1"
            parts = line.split()
            if len(parts) >= 2 and parts[1] == 'device':
                uri = f"Android:///{parts[0]}"

                # 尝试从详细信息中提取 model
                model_match = re.search(r'model:(\S+)', line)
                model = model_match.group(1) if model_match else 'Unknown'

                devices.append({
                    'uri': uri,
                    'serial': parts[0],
                    'status': parts[1],
                    'model': model
                })

        return Response(devices)

    except FileNotFoundError:
        return Response({'error': "未找到 'adb' 命令。请确保ADB已安装并已添加到系统的PATH环境变量中。"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except subprocess.CalledProcessError as e:
        return Response({'error': f"执行 'adb devices' 命令失败: {e.stderr}"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({'error': f"发生未知错误: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def manual_screenshot(request, pk):
    """
    触发一个手动截图任务。
    pk 是任务的ID。
    """
    try:
        task = Task.objects.get(pk=pk)
        if task.status not in ['RUNNING', 'PENDING']:
            return Response({'error': '任务已结束，无法截图'}, status=status.HTTP_400_BAD_REQUEST)

        # 将截图任务放入Celery队列
        take_manual_screenshot_task.delay(task.id)
        return Response({'status': '截图指令已发送'})

    except Task.DoesNotExist:
        return Response({'error': '任务不存在'}, status=status.HTTP_404_NOT_FOUND)