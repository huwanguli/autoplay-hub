from rest_framework import serializers
from .models import Script, Task

class ScriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Script
        fields = '__all__'

class TaskSerializer(serializers.ModelSerializer):
    script_name = serializers.StringRelatedField(source='script.name', read_only=True)

    class Meta:
        model = Task
        read_only_fields = ('status', 'started_at', 'completed_at', 'latest_screenshot','latest_screenshot_url', )

        fields = [
            'id', 'script', 'script_name', 'status', 'log','created_at', 'started_at',
            'completed_at', 'latest_screenshot','latest_screenshot_url'
        ]
