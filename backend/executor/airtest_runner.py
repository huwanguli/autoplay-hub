import os
import time
from django.conf import settings
from airtest.core.api import auto_setup, touch, swipe, sleep, snapshot, Template, text
from airtest.core.error import TargetNotFoundError
from .task_logger import TaskLogger
from api.models import Script


def execute_script_flow(script_content: dict, device_uri: str, logger: TaskLogger):
    """
    v2.0 脚本解释器的总入口。
    """
    # 仅在顶层任务开始时初始化Airtest环境
    # 子脚本执行时将复用这个环境
    auto_setup(logdir=False, devices=[device_uri])
    logger.log(f"Airtest已连接到设备: {device_uri}")

    variables = script_content.get("variables", {})
    steps = script_content.get("steps", [])

    for node in steps:
        _process_node(node, variables, logger)


def _process_node(node: dict, variables: dict, logger: TaskLogger):
    """
    递归处理单个节点。这是解释器的核心分派器。
    """
    node_type = node.get("type")
    description = node.get("description", "无描述")
    logger.log(f"--- [执行节点] {description} (类型: {node_type}) ---")

    if node_type == "action":
        _execute_action_node(node, variables, logger)
    elif node_type == "loop":
        _execute_loop_node(node, variables, logger)
    elif node_type == "condition":
        _execute_condition_node(node, variables, logger)
    # ★ 关键：当节点类型为 sub_script 时，调用我们升级后的子脚本执行器
    elif node_type == "sub_script":
        _execute_sub_script_node(node, variables, logger)
    else:
        logger.log(f"警告：未知的节点类型 '{node_type}'")


def _resolve_value(value, variables):
    """解析参数中的变量引用"""
    if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
        var_name = value[2:-2].strip()
        return variables.get(var_name, value)
    return value


def _execute_action_node(node: dict, variables: dict, logger: TaskLogger):
    """执行单个“动作”节点"""
    action = node.get("action")
    params = node.get("params", {})
    on_failure = node.get("on_failure", "abort")

    resolved_params = {k: _resolve_value(v, variables) for k, v in params.items()}
    logger.log(f"执行动作: {action}，参数: {resolved_params}")

    def perform_action():
        """封装的原子操作，用于重试"""
        if action == "sleep":
            sleep(resolved_params.get("duration", 1))
        elif action == "touch":
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

    # 失败处理逻辑
    try:
        if isinstance(on_failure, dict) and "retry" in on_failure:
            retry_config = on_failure["retry"]
            for i in range(retry_config.get("count", 1)):
                try:
                    perform_action()
                    return
                except TargetNotFoundError as e:
                    logger.log(f"动作失败 (尝试 {i + 1}/{retry_config['count']}): {e}")
                    if i + 1 < retry_config['count']:
                        time.sleep(retry_config.get("delay", 1))
                    else:
                        raise e
        else:
            perform_action()
    except Exception as e:
        logger.log(f"动作失败，准备处理失败策略 '{on_failure}'。错误: {e}")
        if on_failure == "ignore":
            logger.log(f"动作失败，已忽略: {e}")
        else:
            raise e


def _execute_loop_node(node: dict, variables: dict, logger: TaskLogger):
    """执行“循环”节点"""
    if node.get("loop_type") == "count":
        count = node.get("count", 0)
        for i in range(count):
            logger.log(f"--- [循环 {i + 1}/{count}] ---")
            for sub_node in node.get("steps", []):
                _process_node(sub_node, variables, logger)


def _execute_condition_node(node: dict, variables: dict, logger: TaskLogger):
    """执行“条件”节点"""
    condition_met = False
    if node.get("condition_type") == "if_image_exists":
        params = node.get("params", {})
        target_path = os.path.join(settings.BASE_DIR, 'script_assets', params['target'])
        if Template(target_path).exists():
            condition_met = True

    if condition_met:
        logger.log("条件为真 (True)，执行 if_true 分支")
        for sub_node in node.get("if_true", []):
            _process_node(sub_node, variables, logger)
    else:
        logger.log("条件为假 (False)，执行 if_false 分支")
        for sub_node in node.get("if_false", []):
            _process_node(sub_node, variables, logger)


def _execute_sub_script_node(node: dict, variables: dict, logger: TaskLogger):
    """
    ★★★ 全新升级的子脚本执行器 ★★★
    通过数据库ID动态调用并执行另一个脚本。
    """
    params = node.get("params", {})
    resolved_params = {k: _resolve_value(v, variables) for k, v in params.items()}

    sub_script_id = resolved_params.get("id")
    if not sub_script_id:
        raise ValueError("sub_script 节点需要一个 'id' 参数。")

    try:
        # 从数据库中获取子脚本模型
        sub_script_model = Script.objects.get(id=sub_script_id)
        logger.log(f"--- [开始执行子脚本: '{sub_script_model.name}' (ID: {sub_script_id})] ---")

        # 获取子脚本的内容
        sub_script_content = sub_script_model.content
        sub_script_steps = sub_script_content.get("steps", [])

        # ★ 关键：递归处理子脚本中的每一个节点
        for sub_node in sub_script_steps:
            # 我们将父脚本的变量传递给子脚本，未来可以实现更复杂的变量作用域
            _process_node(sub_node, variables, logger)

        logger.log(f"--- [子脚本 '{sub_script_model.name}' 执行完毕] ---")

    except Script.DoesNotExist:
        raise ValueError(f"找不到ID为 {sub_script_id} 的子脚本。")