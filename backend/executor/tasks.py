from celery import shared_task
from django.utils import timezone
from api.models import Task
from .task_logger import TaskLogger
from .airtest_runner import execute_script_flow


@shared_task
def execute_automation_task(task_id: int, device_uri: str):
    """
    接收 task_id 和 device_uri，并协调执行流程。
    """
    logger = TaskLogger(task_id)

    try:
        task = logger.task
        task.started_at = timezone.now()
        logger.log(f"--- [任务开始] 脚本: {task.script.name} ---", status='RUNNING')

        # ★ 关键改动：调用新的执行器，并传入 device_uri
        execute_script_flow(task.script.content, device_uri, logger)

        logger.log(f"--- [任务成功] ---", status='SUCCESS')

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