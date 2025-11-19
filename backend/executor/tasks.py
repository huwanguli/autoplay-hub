from celery import shared_task
from django.utils import timezone
from api.models import Task,Script
from .task_logger import TaskLogger
from .airtest_runner import execute_script_flow
import os
import time
from django.conf import settings
from airtest.core.api import auto_setup,snapshot
from celery.exceptions import SoftTimeLimitExceeded

@shared_task
def execute_automation_task(task_id: int, device_uri: str):
    """
    接收 task_id 和 device_uri，并协调执行流程。
    """
    logger = TaskLogger(task_id)

    def check_for_cancellation():
        """从数据库重新获取任务状态，检查是否已被取消。"""
        # 使用 refresh_from_db 获取最新的状态
        logger.task.refresh_from_db()
        if logger.task.status == 'CANCELED':
            logger.log("检测到任务已被取消，正在终止执行...")
            # 抛出一个异常来中断任务流程
            raise InterruptedError("Task was canceled by user.")

    try:
        task = logger.task
        task.started_at = timezone.now()
        logger.log(f"--- [任务开始] 脚本: {task.script.name} ---", status='RUNNING')

        check_for_cancellation()
        execute_script_flow(task.script.content, device_uri, logger,check_for_cancellation)

        logger.log(f"--- [任务成功] ---", status='SUCCESS')

    except InterruptedError as e:
        # 这是我们自己抛出的异常，表示任务被正常取消了
        print(e)
        # 状态已经在 cancel_task 视图中被设置，这里无需再次操作
        pass

    except Exception as e:
        # 导入我们可能遇到的特定错误
        from airtest.core.error import TargetNotFoundError

        # 记录详细的异常信息
        import traceback
        error_details = traceback.format_exc()
        print(error_details)  # 在Celery控制台打印完整的错误堆栈

        if isinstance(e, TargetNotFoundError):
            logger.log(f"--- [任务失败] 找不到目标图片: {e} ---", status='FAILED')
        else:
            logger.log(f"--- [任务失败] 发生未知错误: {e} ---", status='FAILED')

    return f"任务 {task_id} 执行完毕"

@shared_task
def take_manual_screenshot_task(task_id: int):
    """
    一个专门用于手动截图的轻量级任务。
    它只接收 task_id，然后自己从数据库中查询所有需要的信息。
    """
    try:
        # ★ 1. 从数据库获取任务实例
        task = Task.objects.get(id=task_id)

        # ★ 2. 检查任务是否有关联的 device_uri
        if not task.device_uri:
            print(f"手动截图失败：任务 #{task_id} 没有关联的 device_uri。")
            # 更新日志，让前端也能看到失败原因
            logger = TaskLogger(task.id)
            logger.log("手动截图失败：任务未记录执行设备。")
            return

        print(f"开始为任务 #{task_id} 执行手动截图，设备: {task.device_uri}")

        # ★ 3. 连接设备 (和之前一样)
        auto_setup(logdir=False, devices=[task.device_uri])

        # ★ 4. 生成截图路径 (和之前一样)
        filename = f"manual_snapshot_{int(time.time())}.png"
        snapshot_relative_path = os.path.join('task_logs', str(task.id), filename)
        snapshot_full_path = os.path.join(settings.MEDIA_ROOT, snapshot_relative_path)
        os.makedirs(os.path.dirname(snapshot_full_path), exist_ok=True)

        # ★ 5. 执行截图 (和之前一样)
        snapshot(filename=snapshot_full_path)
        print(f"截图已保存到: {snapshot_full_path}")

        # ★ 6. 更新数据库并触发广播 (和之前一样)
        task.latest_screenshot = snapshot_relative_path
        task.save()

        # 复用 TaskLogger 来进行广播
        logger = TaskLogger(task.id)
        logger.log("手动截图成功。")

    except Task.DoesNotExist:
        print(f"手动截图失败：找不到任务 #{task_id}")
    except Exception as e:
        import traceback
        print(f"手动截图时发生未知错误: {e}")
        traceback.print_exc()
