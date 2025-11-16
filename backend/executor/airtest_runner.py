import os
import time
from django.conf import settings
from airtest.core.api import auto_setup, touch, swipe, sleep, snapshot, Template, text
from airtest.core.error import TargetNotFoundError
from .task_logger import TaskLogger


def execute_script_flow(script_content: dict, device_uri: str, logger: TaskLogger):
    """
    v2.0 脚本解释器的总入口。
    """
    # 1. 初始化 Airtest 环境
    log_dir = os.path.join(settings.MEDIA_ROOT, 'task_logs', str(logger.task_id))
    os.makedirs(log_dir, exist_ok=True)
    auto_setup(__file__, logdir=log_dir, devices=[device_uri])
    logger.log(f"Airtest已连接到设备: {device_uri}")

    # 2. 获取变量和步骤
    variables = script_content.get("variables", {})
    steps = script_content.get("steps", [])

    # 3. 循环执行所有顶层节点
    for node in steps:
        _process_node(node, variables, logger)


def _process_node(node: dict, variables: dict, logger: TaskLogger):
    """
    递归处理单个节点。这是解释器的核心。
    """
    node_type = node.get("type")
    description = node.get("description", "无描述")
    logger.log(f"--- [执行节点] {description} (类型: {node_type}) ---")

    # 根据节点类型分派到不同的处理器
    if node_type == "action":
        _execute_action_node(node, variables, logger)
    elif node_type == "loop":
        _execute_loop_node(node, variables, logger)
    elif node_type == "condition":
        _execute_condition_node(node, variables, logger)
    elif node_type == "sub_script":
        _execute_sub_script_node(node, variables, logger)
    else:
        logger.log(f"警告：未知的节点类型 '{node_type}'")


def _resolve_value(value, variables):
    """解析参数中的变量引用，例如 '{{username}}'"""
    if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
        var_name = value[2:-2].strip()
        return variables.get(var_name, value)  # 如果变量未定义，返回原始字符串
    return value


def _execute_action_node(node: dict, variables: dict, logger: TaskLogger):
    action = node.get("action")
    params = node.get("params", {})
    on_failure = node.get("on_failure", "abort")  # 默认为 abort

    # 解析参数中的变量
    resolved_params = {k: _resolve_value(v, variables) for k, v in params.items()}

    def perform_action():
        """封装的原子操作，用于重试"""
        if action == "sleep":
            sleep(resolved_params.get("duration", 1))
        elif action == "touch":
            target_path = os.path.join(settings.BASE_DIR, 'script_assets', resolved_params['target'])
            touch(Template(target_path))
        elif action == "swipe":
            swipe(tuple(resolved_params['start']), tuple(resolved_params['end']))
        elif action == "text":
            text(resolved_params.get("text", ""))
        elif action == "snapshot":
            filename = resolved_params.get("filename", f"snapshot_{int(time.time())}.png")
            snapshot_path = os.path.join('task_logs', str(logger.task_id), filename)
            snapshot(filename=os.path.join(settings.MEDIA_ROOT, snapshot_path))
            logger.update_screenshot(snapshot_path)
        else:
            raise ValueError(f"未知的原子动作: {action}")

    # 实现失败处理逻辑
    try:
        if isinstance(on_failure, dict) and "retry" in on_failure:
            retry_config = on_failure["retry"]
            for i in range(retry_config.get("count", 1)):
                try:
                    perform_action()
                    return  # 成功则退出
                except TargetNotFoundError as e:
                    logger.log(f"动作失败 (尝试 {i + 1}/{retry_config['count']}): {e}")
                    if i + 1 < retry_config['count']:
                        time.sleep(retry_config.get("delay", 1))
                    else:
                        raise e  # 最后一次尝试失败，重新抛出异常
        else:
            perform_action()  # 无重试配置，直接执行
    except Exception as e:
        if on_failure == "ignore":
            logger.log(f"动作失败，已忽略: {e}")
        else:  # "abort" 或重试后最终失败
            raise e  # 将异常向上传递，由顶层任务捕获


def _execute_loop_node(node: dict, variables: dict, logger: TaskLogger):
    if node.get("loop_type") == "count":
        count = node.get("count", 0)
        for i in range(count):
            logger.log(f"--- [循环 {i + 1}/{count}] ---")
            for sub_node in node.get("steps", []):
                _process_node(sub_node, variables, logger)


def _execute_condition_node(node: dict, variables: dict, logger: TaskLogger):
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
    """在这里实现预定义的子脚本"""
    name = node.get("name")
    params = node.get("params", {})
    resolved_params = {k: _resolve_value(v, variables) for k, v in params.items()}

    if name == "standard_login":
        # 这是一个硬编码的子脚本示例
        logger.log("--- [执行子脚本: standard_login] ---")
        # 假设登录需要点击用户名、输入、点击密码、输入、点击登录
        # 你需要根据你的实际情况提供图片和坐标
        # _execute_action_node(...)
        pass  # 此处需要您根据实际情况填充
    else:
        logger.log(f"警告：未知的子脚本 '{name}'")