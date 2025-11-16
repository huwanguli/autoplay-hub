from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ScriptViewSet, TaskViewSet, list_devices, manual_screenshot, cancel_task

# 创建一个路由器，并注册我们的视图集
router = DefaultRouter()
router.register(r'scripts', ScriptViewSet)
router.register(r'tasks', TaskViewSet)

# API的URL由路由器自动确定
urlpatterns = [
    path('', include(router.urls)),

    path('devices/',list_devices,name='devices-list'),
    path('tasks/<int:pk>/screenshot/', manual_screenshot, name='task-screenshot'),

    path('tasks/<int:pk>/cancel/', cancel_task, name='task-cancel'),
]