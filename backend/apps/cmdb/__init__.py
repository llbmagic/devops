"""CMDB 资产管理模块.

提供运维平台的核心资产数据模型，包括业务线、环境、应用、集群、主机等
资产管理功能，支撑 2000+ 主机的统一纳管。

公开子模块:
    - models: BusinessLine, Environment, Application, Cluster, Tag, Host, ApplicationDependency
    - serializers: 各模型的序列化器
    - views: REST API 视图集
    - urls: 路由配置

数据模型层次结构:
    业务线 (BusinessLine)
        └── 应用 (Application)
              └── 集群 (Cluster)
                    └── 主机 (Host)

典型使用场景:
    - 按业务线统计主机数量
    - 按环境和应用组织集群
    - 追踪应用间依赖关系
    - 主机标签化管理

示例:
    >>> from apps.cmdb.models import BusinessLine, Host
    >>> bl = BusinessLine.objects.create(name='电商平台')
"""

# 显式导出公开子模块（延迟导入，避免 AppRegistryNotReady）
__all__ = [
    'BusinessLine',
    'Environment',
    'Application',
    'Cluster',
    'Tag',
    'Host',
    'ApplicationDependency',
    'BusinessLineSerializer',
    'EnvironmentSerializer',
    'ApplicationSerializer',
    'ClusterSerializer',
    'TagSerializer',
    'HostSerializer',
    'ApplicationDependencySerializer',
    'BusinessLineViewSet',
    'EnvironmentViewSet',
    'ApplicationViewSet',
    'ClusterViewSet',
    'TagViewSet',
    'HostViewSet',
    'ApplicationDependencyViewSet',
]
