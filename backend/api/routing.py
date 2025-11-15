from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # 将 ws/task-updates/ 这个URL路径映射到我们的TaskStatusConsumer
    re_path(r'ws/task-updates/$', consumers.TaskStatusConsumer.as_asgi()),
]