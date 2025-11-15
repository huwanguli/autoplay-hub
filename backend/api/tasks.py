import os
import json
from celery import shared_task
from django.utils import timezone
from django.conf import settings
from .models import Task
from .serializers import TaskSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from airtest.core.api import (
    auto_setup,
    start_app,
    touch,
    swipe,
    sleep,
    snapshot,
    Template,
)
from airtest.core.error import TargetNotFoundError

@shared_task
def execute_automation_task(task_id):
    """
    一个Celery任务，用于执行单个自动化任务 (终极修正版)
    """
    task = None
    channel_layer = get_channel_layer()
    log_content = ""  # 我们用一个字符串来累积日志

    def broadcast_status(task_instance, new_log_line=None):
        """
        一个经过简化的辅助函数，用于更新日志、保存并广播状态。
        """
        nonlocal log_content
        if new_log_line:
            print(new_log_line)  # 仍然在控制台打印
            log_content += new_log_line + "\n"
            task_instance.log = log_content  # 将累积的日志更新到task实例上

        task_instance.save()  # ★ 关键：在发送前，保存所有更改（状态、日志、截图路径）

        serializer = TaskSerializer(task_instance)
        async_to_sync(channel_layer.group_send)(
            'task_updates',
            {
                'type': 'task.update',
                'message': serializer.data
            }
        )

    try:
        # 1. 获取任务对象并更新初始状态
        task = Task.objects.get(id=task_id)
        task.status = 'RUNNING'
        task.started_at = timezone.now()
        broadcast_status(task, new_log_line=f"--- [任务开始] 任务ID: {task.id}, 脚本: {task.script.name} ---")

        # 2. 解析脚本内容
        script_content = task.script.content
        device_uri = script_content.get("device", "Android:///")
        steps = script_content.get("steps", [])

        # 3. 设置Airtest运行环境
        log_dir = os.path.join(settings.MEDIA_ROOT, 'task_logs', str(task.id))
        os.makedirs(log_dir, exist_ok=True)
        auto_setup(__file__, logdir=log_dir, devices=[device_uri])
        broadcast_status(task, new_log_line=f"Airtest已连接到设备: {device_uri}")

        # 4. 循环执行每一步
        for i, step in enumerate(steps):
            broadcast_status(task, new_log_line=f"--- [步骤 {i + 1}/{len(steps)}] {step.get('description', '')} ---")
            action = step.get("action")
            params = step.get("params", {})

            # ... [touch, swipe, sleep 等动作保持不变] ...
            if action == "sleep":
                sleep(params.get("duration", 1))
            elif action == "touch":
                image_path = os.path.join(settings.BASE_DIR, 'script_assets', params['target'])
                touch(Template(image_path))
            elif action == "swipe":
                swipe(tuple(params['start']), tuple(params['end']))
            elif action == "snapshot":
                filename = params.get("filename", f"snapshot_{timezone.now().strftime('%H%M%S')}.png")
                snapshot_path_relative = os.path.join('task_logs', str(task.id), filename)
                snapshot_path_full = os.path.join(settings.MEDIA_ROOT, snapshot_path_relative)
                snapshot(filename=snapshot_path_full)

                # 更新截图字段，并调用广播
                task.latest_screenshot = snapshot_path_relative
                broadcast_status(task, new_log_line=f"截图已保存到: {snapshot_path_relative}")
            else:
                broadcast_status(task, new_log_line=f"警告：未知的动作 '{action}'")

        # 5. 执行成功
        task.status = 'SUCCESS'
        broadcast_status(task, new_log_line=f"\n--- [任务成功] 任务ID: {task.id} ---")

    except Exception as e:
        if task:
            task.status = 'FAILED'
            broadcast_status(task, new_log_line=f"\n--- [任务失败] 发生错误: {e} ---")
    finally:
        if task:
            task.completed_at = timezone.now()
            # 发送最后一次包含完成时间的更新
            broadcast_status(task, new_log_line="--- [任务结束] ---")

    return f"任务 {task_id} 执行完毕"