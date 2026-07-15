"""GitLab 模块序列化器.

提供 GitLab 各模型的序列化器，用于 API 数据的序列化和反序列化。

主要序列化器:
    - GitLabInstanceSerializer: GitLab 实例序列化器
    - ProjectSerializer: 代码仓库序列化器
    - MergeRequestSerializer: 合并请求序列化器

使用示例:
    >>> from apps.gitlab.serializers import GitLabInstanceSerializer
    >>> from apps.gitlab.models import GitLabInstance
    >>> instance = GitLabInstance.objects.first()
    >>> serializer = GitLabInstanceSerializer(instance)
    >>> print(serializer.data)
"""

from rest_framework import serializers
from .models import GitLabInstance, Project, MergeRequest


class GitLabInstanceSerializer(serializers.ModelSerializer):
    """GitLab 实例序列化器.

    用于序列化 GitLab 实例模型，包含名称、URL、启用状态等信息。
    access_token 字段设置为 write_only，仅在创建/更新时写入，不在响应中返回。

    示例:
        >>> serializer = GitLabInstanceSerializer(instance)
        >>> serializer.data
        {'id': 1, 'name': '公司 GitLab', 'url': 'https://gitlab.example.com',
         'is_active': True, 'created_at': '2024-01-01T00:00:00Z'}
    """

    class Meta:
        """序列化器元数据."""
        model = GitLabInstance
        fields = '__all__'
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'access_token': {'write_only': True}
        }


class ProjectSerializer(serializers.ModelSerializer):
    """代码仓库序列化器.

    用于序列化项目模型，提供关联实例名称等附加字段。

    新增字段:
        instance_name: 所属实例名称（只读）。

    示例:
        >>> serializer = ProjectSerializer(project)
        >>> serializer.data
        {'id': 1, 'instance': 1, 'instance_name': '公司 GitLab',
         'gitlab_id': 123, 'name': 'my-project', ...}
    """

    instance_name = serializers.CharField(
        source='instance.name',
        read_only=True,
        help_text='所属实例名称'
    )

    class Meta:
        """序列化器元数据."""
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class MergeRequestSerializer(serializers.ModelSerializer):
    """合并请求序列化器.

    用于序列化 MR 模型，提供关联项目和实例的详细信息。

    新增字段:
        project_name: 所属项目名称（只读）。
        project_path: 所属项目完整路径（只读）。

    示例:
        >>> serializer = MergeRequestSerializer(mr)
        >>> serializer.data
        {'id': 1, 'project': 1, 'project_name': 'my-project',
         'project_path': 'group/my-project', 'gitlab_id': 1, ...}
    """

    project_name = serializers.CharField(
        source='project.name',
        read_only=True,
        help_text='所属项目名称'
    )
    project_path = serializers.CharField(
        source='project.path_with_namespace',
        read_only=True,
        help_text='所属项目路径'
    )

    class Meta:
        """序列化器元数据."""
        model = MergeRequest
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
