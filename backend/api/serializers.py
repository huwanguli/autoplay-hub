from django.conf import settings
from rest_framework import serializers
from .models import Script, Task

class ScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Script
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    # 使用 StringRelatedField 来显示脚本名称，而不是ID，更具可读性
    script_name = serializers.StringRelatedField(source='script.name', read_only=True)
    #latest_screenshot_url = serializers.SerializerMethodField()
    class Meta:
        model = Task
        read_only_fields = ('status', 'started_at', 'completed_at', 'latest_screenshot','latest_screenshot_url', )

        fields = [
            'id', 'script', 'script_name', 'status', 'log','created_at', 'started_at',
            'completed_at', 'latest_screenshot','latest_screenshot_url'
        ]
