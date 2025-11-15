from django.conf import settings
from rest_framework import serializers
from .models import Script, Task

class ScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Script
        fields = '__all__'  # 包含所有字段

class TaskSerializer(serializers.ModelSerializer):
    # 使用 StringRelatedField 来显示脚本名称，而不是ID，更具可读性
    script_name = serializers.StringRelatedField(source='script.name', read_only=True)
    #latest_screenshot_url = serializers.SerializerMethodField()
    class Meta:
        model = Task
        # read_only_fields 用于指定只能通过后端逻辑修改，不能通过API直接创建/更新的字段
        read_only_fields = ('status', 'started_at', 'completed_at', 'latest_screenshot','latest_screenshot_url', )

        # 在返回的JSON中包含所有字段
        fields = [
            'id', 'script', 'script_name', 'status', 'log','created_at', 'started_at',
            'completed_at', 'latest_screenshot','latest_screenshot_url'
        ]

    # def get_latest_screenshot_url(self, obj):
    #     if obj.latest_screenshot:
    #         request = self.context.get('request')
    #         if request:
    #             return request.build_absolute_uri(settings.MEDIA_URL + obj.latest_screenshot)
    #             # 如果没有request上下文（比如在shell中序列化），则返回相对路径
    #         return settings.MEDIA_URL + obj.latest_screenshot
    #     return None