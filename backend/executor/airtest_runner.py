import os
import time
from django.conf import settings
from airtest.core.api import auto_setup, touch, swipe, sleep, snapshot, Template, text, exists
from airtest.core.error import TargetNotFoundError
from .task_logger import TaskLogger


def execute_script_flow(script_content: dict, device_uri: str, logger: TaskLogger, cancellation_check_func=None):
    # 移除了 ST.FIND_TIMEOUT 的设置
    auto_setup(logdir=False, devices=[device_uri])
    logger.log(f"Airtest已连接到设备: {device_uri}")
    variables = script_content.get("variables", {})
    steps = script_content.get("steps", [])
    for node in steps:
        if cancellation_check_func:
            cancellation_check_func()
        _process_node(node, variables, logger, cancellation_check_func)


# _process_node 和 _resolve_value 函数无变化
def _process_node(node: dict, variables: dict, logger: TaskLogger, cancellation_check_func=None):
    node_type = node.get("type")
    description = node.get("description", "无描述")
    logger.log(f"--- [执行节点] {description} (类型: {node_type}) ---")
    if node_type == "action":
        _execute_action_node(node, variables, logger, cancellation_check_func)
    elif node_type == "loop":
        _execute_loop_node(node, variables, logger, cancellation_check_func)
    elif node_type == "condition":
        _execute_condition_node(node, variables, logger, cancellation_check_func)
    else:
        logger.log(f"警告：跳过未知的节点类型 '{node_type}'")


def _resolve_value(value, variables):
    if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
        var_name = value[2:-2].strip()
        return variables.get(var_name, value)
    return value


def _execute_action_node(node: dict, variables: dict, logger: TaskLogger, cancellation_check_func=None):
    max_step_retries = 3
    step_retry_count = 0
    while step_retry_count <= max_step_retries:
        if step_retry_count > 0:
            logger.log(f"--- [步骤重试 {step_retry_count}/{max_step_retries}] ---")

        action = node.get("action")
        params = node.get("params", {})
        on_action_failure = node.get("on_failure", "abort")
        resolved_params = {k: _resolve_value(v, variables) for k, v in params.items()}
        logger.log(f"执行动作: {action}，参数: {resolved_params}")

        try:
            def perform_action():
                if action == "sleep":
                    duration = resolved_params.get("duration", 1)
                    # ★ 统一使用 airtest.sleep
                    for _ in range(int(duration)):
                        if cancellation_check_func: cancellation_check_func()
                        sleep(1)
                    remaining_sleep = duration - int(duration)
                    if remaining_sleep > 0: sleep(remaining_sleep)
                elif action == "touch":
                    # ★ 回溯: 恢复到直接调用 touch，让 Airtest 自行处理查找
                    target_path = os.path.join(settings.BASE_DIR, 'script_assets', resolved_params['target'])
                    touch(Template(target_path))
                elif action == "swipe":
                    start_pos = tuple(resolved_params['start'])
                    end_pos = tuple(resolved_params['end'])
                    swipe(start_pos, end_pos)
                elif action == "text":
                    text_to_input = resolved_params.get("content", "")
                    text(text_to_input)
                elif action == "snapshot":
                    filename = resolved_params.get("filename", f"snapshot_{int(time.time())}.png")
                    snapshot_path = os.path.join('task_logs', str(logger.task_id), filename)
                    snapshot(filename=os.path.join(settings.MEDIA_ROOT, snapshot_path))
                    logger.update_screenshot(snapshot_path)
                else:
                    raise ValueError(f"未知的原子动作: {action}")

            if isinstance(on_action_failure, dict) and "retry" in on_action_failure:
                # ... (重试逻辑保持不变)
                retry_config = on_action_failure["retry"]
                for i in range(retry_config.get("count", 1) + 1):
                    try:
                        perform_action()
                        break
                    except TargetNotFoundError as e:
                        if i < retry_config.get("count", 1):
                            logger.log(f"动作失败 (尝试 {i + 1}/{retry_config['count']}): {e}")
                            sleep(retry_config.get("delay", 1))
                        else:
                            raise e
            else:
                perform_action()
        except Exception as e:
            # ... (异常处理逻辑不变)
            if isinstance(e, InterruptedError): raise e
            logger.log(f"动作执行失败，策略: '{on_action_failure}'。错误: {e}")
            if on_action_failure == "ignore":
                logger.log(f"动作失败，已忽略。")
                return
            else:
                raise e

        validation_node = node.get("validate")
        if not validation_node:
            logger.log("步骤无验证环节，执行成功。")
            return

        # ... (validate 验证逻辑不变，但内部使用的是正确的 exists 函数)
        logger.log(f"开始执行验证...")
        v_type = validation_node.get("type")
        v_target = validation_node.get("target")
        v_timeout = validation_node.get("timeout", 5)
        v_on_failure = validation_node.get("on_failure", "abort")
        is_valid = False
        start_time = time.time()
        while time.time() - start_time < v_timeout:
            if cancellation_check_func: cancellation_check_func()
            if v_type == "image_exists":
                target_path = os.path.join(settings.BASE_DIR, 'script_assets', v_target)
                if exists(Template(target_path)):
                    is_valid = True
                    logger.log(f"验证成功：图片 '{v_target}' 已在屏幕上找到。")
                    break
            sleep(1)

        if is_valid:
            return

        logger.log(f"验证失败：在 {v_timeout} 秒内未能满足条件。")
        if v_on_failure == "retry_step":
            step_retry_count += 1
            if step_retry_count < max_step_retries:
                logger.log("策略为 'retry_step'，准备重试整个步骤。")
                continue
            else:
                logger.log(f"已达到最大步骤重试次数 ({max_step_retries})，任务中止。")
                raise ValueError("验证失败且已达到最大重试次数。")
        elif v_on_failure == "ignore":
            logger.log("策略为 'ignore'，已忽略验证失败。")
            return
        else:
            raise ValueError("验证失败，任务中止。")


def _execute_loop_node(node: dict, variables: dict, logger: TaskLogger, cancellation_check_func=None):
    # ... (此函数无变化) ...
    if node.get("loop_type") == "count":
        count = node.get("count", 0)
        for i in range(count):
            if cancellation_check_func: cancellation_check_func()
            logger.log(f"--- [循环 {i + 1}/{count}] ---")
            for sub_node in node.get("steps", []):
                _process_node(sub_node, variables, logger, cancellation_check_func)


def _execute_condition_node(node: dict, variables: dict, logger: TaskLogger, cancellation_check_func=None):
    # ... (此函数无变化, 内部使用正确的 exists 函数) ...
    condition_met = False
    if node.get("condition_type") == "if_image_exists":
        params = node.get("params", {})
        target_path = os.path.join(settings.BASE_DIR, 'script_assets', params['target'])
        if exists(Template(target_path)):
            condition_met = True

    if condition_met:
        logger.log("条件为真 (True)，执行 if_true 分支")
        for sub_node in node.get("if_true", []):
            if cancellation_check_func: cancellation_check_func()
            _process_node(sub_node, variables, logger, cancellation_check_func)
    else:
        logger.log("条件为假 (False)，执行 if_false 分支")
        for sub_node in node.get("if_false", []):
            if cancellation_check_func: cancellation_check_func()
            _process_node(sub_node, variables, logger, cancellation_check_func)
