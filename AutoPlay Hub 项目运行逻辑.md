# AutoPlay Hub 项目运行逻辑

AutoPlay Hub 是基于**前后端分离 + 异步任务处理**架构的自动化脚本运行平台，本文档将详细拆解平台核心组件及「运行脚本」操作的完整生命周期，帮助开发者理解项目内部的协同逻辑。

# 一、核心组件说明

平台由 5 个核心模块协同工作，各模块的角色和技术栈如下：

|核心组件|技术栈|角色定位|
|---|---|---|
|前端|Vue.js (Pinia/Router)|可视化操作界面（驾驶舱）|
|后端 API 服务器|Django REST Framework|指令接收/数据库管理（调度总机）|
|消息队列|Redis|异步任务暂存（任务等候室）|
|后台工作进程|Celery Worker|异步任务执行（后台工人/机器人）|
|实时通信|Channels + WebSockets|任务状态实时推送（广播系统）|
# 二、「运行一个脚本」操作全生命周期

以下以「选择脚本并点击运行」为例，拆解从前端操作到任务完成的完整流程。

## 阶段 1：前端 - 发出指令（驾驶舱下达操作）

1. **页面初始化**：打开平台主页时，`AutomationHubView.vue` 组件加载，`onMounted` 钩子触发，调用 `scriptStore/fetchScripts` 和 `deviceStore/fetchDevices` 动作，通过 `api.js` 向后端发送 GET 请求：
- 脚本列表：`/api/scripts/`
- 设备列表：`/api/devices/`
请求成功后，前端渲染脚本/设备列表。

2. **用户操作触发**：选择脚本（如 ID=7）和设备（如 `emulator-5554`），点击「运行」按钮，触发组件 `@click` 事件，调用 `scriptStore.runScript` 动作并传入参数：`scriptId: 7`、`deviceUri: 'Android:///emulator-5554'`。

3. **发送 HTTP 请求**：`scriptStore.runScript` 调用 `api.js` 中的 `runScript` 方法，通过 axios 发送 POST 请求：
- 请求地址：`http://localhost:8000/api/scripts/7/run/`
- 请求体（JSON）：
`{ "device_uri": "Android:///emulator-5554" }`

4. **跳转任务详情页**：前端不等待任务完成，从 API 响应中获取新创建的任务 ID（如 52），通过 Vue Router 立即跳转到 `/tasks/52`，页面显示「加载中...」，等待任务状态推送。

## 阶段 2：后端 API - 接收并分派任务（调度总机登记）

1. **请求路由匹配**：Django 服务器接收 POST 请求，通过 URL 路由规则指向 `api/views.py` 中 `ScriptViewSet` 的 `run` 方法。

2. **任务初始化登记**：
- 解析请求体中的 `device_uri`；
- 在数据库 `Task` 表中创建新记录，状态设为 `PENDING`，关联脚本 ID 和设备 URI（示例任务 ID=52）；
- 将新创建的 Task 对象序列化为 JSON，作为 HTTP 响应返回给前端（包含任务 ID=52）。

3. **异步任务分发**：
- 执行 `execute_automation_task.delay(52, device_uri)`（Celery 异步调用）；
- Celery 将任务指令序列化后存入 Redis（任务等候室），并生成唯一 Celery 任务 ID（如 `1db64048-xxxx`），写入 Task 记录的 `celery_task_id` 字段；
- API 服务器完成请求处理，释放资源处理其他请求。

## 阶段 3：后台工人 - 领取并执行任务（车间干活）

1. **任务监听与领取**：后台运行的 Celery Worker 进程（`celery -A backend worker ...`）持续监听 Redis，发现新任务后取下「任务便签」，反序列化得到待执行函数 `execute_automation_task` 及参数 `(52, "Android:///emulator-5554")`。

2. **任务执行流程**：
- 初始化日志器：`logger = TaskLogger(52)`（用于更新数据库和广播状态）；
- 更新任务状态为 `RUNNING`，并通过 `logger` 首次广播状态；
- 调用 `airtest_runner.py` 中的 `execute_script_flow`，传入脚本内容、设备 URI、logger 和取消检查函数；
- `airtest_runner.py` 中的 `_process_node`、`_execute_action_node` 等函数递归执行 JSON 脚本的每一步（如 `touch`/`sleep`/`swipe`），通过 ADB 与设备进行真实交互。

## 阶段 4：实时广播 - 车间向驾驶舱实时汇报

1. **日志产生与推送**：脚本执行过程中，每一步操作都会调用 `logger.log("日志内容")`，`TaskLogger.log` 方法执行两项操作：
- 数据库更新：将日志追加到 Task 表 ID=52 记录的 `log` 字段；
- 实时广播：通过 Channels 库将完整的 Task 对象（含最新日志）序列化为 JSON，通过 WebSocket 推送到 `task_updates` 频道。

2. **前端接收与渲染**：
- `TaskDetailView.vue` 在 `onMounted` 时建立 WebSocket 连接，监听 `task.update` 消息；
- 收到消息后更新 Pinia `taskDetailStore` 中的 `task` 对象；
- 基于 Vue 响应式特性，页面日志、截图等内容自动更新，无需刷新。

## 阶段 5：任务完成

1. 脚本执行完毕后，`execute_automation_task` 调用 `logger.log("--- [任务成功] ---", status='SUCCESS')`；
2. `TaskLogger` 将任务状态更新为 `SUCCESS`，记录完成时间并发送最后一次广播；
3. 前端接收最终状态，将状态标签渲染为绿色，隐藏「取消任务」按钮，任务流程结束。

# 三、总结

AutoPlay Hub 通过「前后端分离 + 异步任务 + 实时通信」的架构设计，实现了：
- 前端无阻塞操作（无需等待耗时任务完成）；
- 后端任务解耦（API 服务器不处理耗时操作）；
- 实时状态反馈（日志/截图即时更新）。

整个流程中，数据从前端发起请求，经后端分发到异步队列，由 Celery Worker 执行，最终通过 WebSocket 将结果实时推回前端，形成完整的闭环。
> （注：文档部分内容可能由 AI 生成）