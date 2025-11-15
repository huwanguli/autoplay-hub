import json
from channels.generic.websocket import AsyncWebsocketConsumer

class TaskStatusConsumer(AsyncWebsocketConsumer):
    # 定义一个组名，所有客户端都将加入这个组
    GROUP_NAME = 'task_updates'

    async def connect(self):
        print(">>> [Consumer] WebSocket connect()方法被调用。")
        try:
            print(">>> [Consumer] 准备加入组...")
            await self.channel_layer.group_add(
                self.GROUP_NAME,
                self.channel_name
            )
            print(">>> [Consumer] 成功加入组！")
        except Exception as e:
            print(f">>> [Consumer] 加入组时发生严重错误: {e}")
            # 如果出错了，拒绝连接
            await self.close()
            return

        await self.accept()
        print(f">>> [Consumer] WebSocket连接已接受！客户端: {self.channel_name}")

    async def disconnect(self, close_code):
        """当WebSocket连接断开时调用"""
        # 将当前连接从组中移除
        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )
        print(f"WebSocket客户端 {self.channel_name} 已断开")

    async def task_update(self, event):
        """
        这是一个自定义的事件处理器。
        当从频道层收到类型为'task.update'的消息时，这个方法会被调用。
        """
        # 将从频道层收到的消息，通过WebSocket发送给前端客户端
        await self.send(text_data=json.dumps(event['message']))
        print(f"已向客户端发送任务更新: {event['message']}")
