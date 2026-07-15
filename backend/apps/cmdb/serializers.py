"""CMDB 模块序列化器.

提供 CMDB 各模型的序列化器，用于 API 数据的序列化和反序列化。
序列化器负责将 Django 模型实例转换为 JSON 格式，以及验证输入数据。

主要序列化器:
    - TagSerializer: 标签序列化器
    - BusinessLineSerializer: 业务线序列化器（含主机数量统计）
    - EnvironmentSerializer: 环境序列化器
    - ApplicationSerializer: 应用序列化器（含集群数量统计）
    - ClusterSerializer: 集群序列化器（含主机数量统计）
    - HostSerializer: 主机序列化器（含业务线、集群、标签详情）
    - ApplicationDependencySerializer: 应用依赖序列化器

使用示例:
    >>> from apps.cmdb.serializers import HostSerializer
    >>> from apps.cmdb.models import Host
    >>> host = Host.objects.first()
    >>> serializer = HostSerializer(host)
    >>> print(serializer.data)
"""

from rest_framework import serializers
from .models import BusinessLine, Environment, Application, Cluster, Tag, Host, ApplicationDependency


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器.

    用于序列化标签模型，包含 tag 的 key 和 value。
    """

    class Meta:
        """序列化器元数据.

        属性:
            model: 对应的模型类。
            fields: 序列化的字段，'__all__' 表示所有字段。
        """
        model = Tag
        fields = '__all__'


class BusinessLineSerializer(serializers.ModelSerializer):
    """业务线序列化器.

    序列化业务线模型，并提供主机数量统计字段。
    新增字段:
        host_count: 该业务线下的主机总数。

    示例:
        >>> serializer = BusinessLineSerializer(business_line)
        >>> serializer.data
        {'id': 1, 'name': '电商平台', 'host_count': 10, ...}
    """

    host_count = serializers.SerializerMethodField(
        help_text='该业务线下的主机总数'
    )

    class Meta:
        """序列化器元数据."""
        model = BusinessLine
        fields = '__all__'

    def get_host_count(self, obj: BusinessLine) -> int:
        """获取该业务线下的主机数量.

        通过反向查询 host_set 统计主机数量。

        Args:
            obj: 业务线模型实例。

        Returns:
            该业务线下的主机数量。
        """
        return obj.host_set.count()


class EnvironmentSerializer(serializers.ModelSerializer):
    """环境序列化器.

    用于序列化环境模型，包含环境的名称、代码、描述和排序信息。
    """

    class Meta:
        """序列化器元数据."""
        model = Environment
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    """应用序列化器.

    序列化应用模型，提供业务线名称和集群数量统计。
    新增字段:
        business_line_name: 所属业务线的名称（只读）。
        cluster_count: 该应用下的集群总数（只读）。

    示例:
        >>> serializer = ApplicationSerializer(application)
        >>> serializer.data
        {'id': 1, 'name': '用户服务', 'business_line_name': '电商平台', 'cluster_count': 3, ...}
    """

    business_line_name = serializers.CharField(
        source='business_line.name',
        read_only=True,
        help_text='所属业务线的名称'
    )
    cluster_count = serializers.SerializerMethodField(
        help_text='该应用下的集群总数'
    )

    class Meta:
        """序列化器元数据."""
        model = Application
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_cluster_count(self, obj: Application) -> int:
        """获取该应用下的集群数量.

        通过反向查询 cluster_set 统计集群数量。

        Args:
            obj: 应用模型实例。

        Returns:
            该应用下的集群数量。
        """
        return obj.cluster_set.count()


class ClusterSerializer(serializers.ModelSerializer):
    """集群序列化器.

    序列化集群模型，提供应用名称、环境名称和主机数量统计。
    新增字段:
        application_name: 所属应用名称（只读）。
        environment_name: 所属环境名称（只读）。
        host_count: 该集群下的主机总数（只读）。

    示例:
        >>> serializer = ClusterSerializer(cluster)
        >>> serializer.data
        {'id': 1, 'name': '用户服务-Dev', 'application_name': '用户服务',
         'environment_name': '开发环境', 'host_count': 5, ...}
    """

    application_name = serializers.CharField(
        source='application.name',
        read_only=True,
        help_text='所属应用名称'
    )
    environment_name = serializers.CharField(
        source='environment.name',
        read_only=True,
        help_text='所属环境名称'
    )
    host_count = serializers.SerializerMethodField(
        help_text='该集群下的主机总数'
    )

    class Meta:
        """序列化器元数据."""
        model = Cluster
        fields = '__all__'

    def get_host_count(self, obj: Cluster) -> int:
        """获取该集群下的主机数量.

        通过反向查询 host_set 统计主机数量。

        Args:
            obj: 集群模型实例。

        Returns:
            该集群下的主机数量。
        """
        return obj.host_set.count()


class HostSerializer(serializers.ModelSerializer):
    """主机序列化器.

    序列化主机模型，提供关联对象的详细名称和标签详情。
    新增字段:
        business_line_name: 所属业务线名称（只读）。
        cluster_name: 所属集群名称（只读）。
        cluster_code: 所属集群代码（只读）。
        tags_detail: 标签详情列表（只读）。

    示例:
        >>> serializer = HostSerializer(host)
        >>> serializer.data
        {'id': 1, 'hostname': 'web-01', 'business_line_name': '电商平台',
         'cluster_name': '用户服务-Dev', 'tags_detail': [{'key': 'env', 'value': 'dev'}], ...}
    """

    business_line_name = serializers.CharField(
        source='business_line.name',
        read_only=True,
        help_text='所属业务线名称'
    )
    cluster_name = serializers.CharField(
        source='cluster.name',
        read_only=True,
        help_text='所属集群名称'
    )
    cluster_code = serializers.CharField(
        source='cluster.code',
        read_only=True,
        help_text='所属集群代码'
    )
    tags_detail = TagSerializer(
        source='tags',
        many=True,
        read_only=True,
        help_text='主机标签详情列表'
    )

    class Meta:
        """序列化器元数据."""
        model = Host
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ApplicationDependencySerializer(serializers.ModelSerializer):
    """应用依赖关系序列化器.

    序列化应用依赖关系，提供应用名称和被依赖应用名称。
    新增字段:
        application_name: 依赖方应用名称（只读）。
        depends_on_name: 被依赖应用名称（只读）。

    示例:
        >>> serializer = ApplicationDependencySerializer(dep)
        >>> serializer.data
        {'id': 1, 'application_name': '用户服务', 'depends_on_name': '支付服务', ...}
    """

    application_name = serializers.CharField(
        source='application.name',
        read_only=True,
        help_text='依赖方应用名称'
    )
    depends_on_name = serializers.CharField(
        source='depends_on.name',
        read_only=True,
        help_text='被依赖应用名称'
    )

    class Meta:
        """序列化器元数据."""
        model = ApplicationDependency
        fields = '__all__'
