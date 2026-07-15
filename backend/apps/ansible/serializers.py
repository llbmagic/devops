"""Ansible 模块序列化器.

提供 Ansible 各模型的序列化器。
"""

from typing import Optional
from rest_framework import serializers
from .models import AnsibleServer, Playbook, TaskRecord


class AnsibleServerSerializer(serializers.ModelSerializer):
    """Ansible 控制节点序列化器.

    用于序列化 Ansible 控制节点模型。
    ssh_password 字段设置为 write_only。

    示例:
        >>> serializer = AnsibleServerSerializer(server)
        >>> serializer.data
        {'id': 1, 'name': 'Ansible Controller', 'host': '192.168.1.100', ...}
    """

    class Meta:
        """序列化器元数据."""
        model = AnsibleServer
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'ssh_password': {'write_only': True}
        }


class PlaybookSerializer(serializers.ModelSerializer):
    """剧本序列化器.

    用于序列化剧本模型，提供创建人用户名和执行次数统计。

    新增字段:
        created_by_username: 创建人用户名（只读）。
        task_count: 该剧本被执行的总次数（只读）。

    示例:
        >>> serializer = PlaybookSerializer(playbook)
        >>> serializer.data
        {'id': 1, 'name': '部署 Web', 'created_by_username': 'admin', 'task_count': 5, ...}
    """

    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True,
        help_text='创建人用户名'
    )
    task_count = serializers.SerializerMethodField(
        help_text='该剧本被执行的总次数'
    )

    class Meta:
        """序列化器元数据."""
        model = Playbook
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_task_count(self, obj: Playbook) -> int:
        """获取该剧本的执行次数."""
        return obj.task_records.count()


class TaskRecordSerializer(serializers.ModelSerializer):
    """任务执行记录序列化器.

    用于序列化任务执行记录模型，提供关联对象的名称和持续时间。

    新增字段:
        playbook_name: 剧本名称（只读）。
        server_name: 控制节点名称（只读）。
        duration: 执行持续时间（秒，只读）。

    示例:
        >>> serializer = TaskRecordSerializer(record)
        >>> serializer.data
        {'id': 1, 'playbook_name': '部署 Web', 'server_name': 'Ansible Controller',
         'duration': 120.5, 'status': 'success', ...}
    """

    playbook_name = serializers.CharField(
        source='playbook.name',
        read_only=True,
        help_text='剧本名称'
    )
    server_name = serializers.CharField(
        source='server.name',
        read_only=True,
        help_text='控制节点名称'
    )
    duration = serializers.SerializerMethodField(
        help_text='执行持续时间（秒）'
    )

    class Meta:
        """序列化器元数据."""
        model = TaskRecord
        fields = '__all__'
        read_only_fields = ['id', 'started_at']

    def get_duration(self, obj: TaskRecord) -> Optional[float]:
        """计算执行持续时间."""
        if obj.finished_at and obj.started_at:
            return (obj.finished_at - obj.started_at).total_seconds()
        return None
