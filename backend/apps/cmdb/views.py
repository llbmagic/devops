"""CMDB 模块视图集.

提供 CMDB 各模型的 ViewSet，实现 RESTful API 接口。
每个 ViewSet 对应一个模型，提供标准的 CRUD 操作。

视图集列表:
    - BusinessLineViewSet: 业务线视图集，完整 CRUD
    - EnvironmentViewSet: 环境视图集，完整 CRUD
    - ApplicationViewSet: 应用视图集，完整 CRUD，支持按业务线筛选
    - ClusterViewSet: 集群视图集，完整 CRUD，支持按应用和环境筛选
    - TagViewSet: 标签视图集，完整 CRUD
    - HostViewSet: 主机视图集，完整 CRUD，支持按业务线、集群、状态筛选
      附加动作:
        - update_tags: 更新单个主机的标签
        - batch_update_tags: 批量更新主机标签
    - ApplicationDependencyViewSet: 应用依赖视图集，完整 CRUD

认证说明:
    所有视图集默认要求登录认证（IsAuthenticated）。
    未认证请求会返回 401 Unauthorized。

使用示例:
    # 获取业务线列表
    GET /api/cmdb/business-lines/

    # 获取主机列表（按集群筛选）
    GET /api/cmdb/hosts/?cluster=1

    # 更新主机标签
    POST /api/cmdb/hosts/1/update_tags/
    Body: {"tag_ids": [1, 2, 3]}
"""

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import BusinessLine, Environment, Application, Cluster, Tag, Host, ApplicationDependency
from .serializers import (
    BusinessLineSerializer, EnvironmentSerializer, ApplicationSerializer,
    ClusterSerializer, TagSerializer, HostSerializer, ApplicationDependencySerializer
)


class BusinessLineViewSet(viewsets.ModelViewSet):
    """业务线视图集.

    提供业务线的完整 CRUD 操作。

    路由:
        GET /api/cmdb/business-lines/ - 获取业务线列表
        POST /api/cmdb/business-lines/ - 创建新业务线
        GET /api/cmdb/business-lines/{id}/ - 获取业务线详情
        PUT /api/cmdb/business-lines/{id}/ - 更新业务线
        DELETE /api/cmdb/business-lines/{id}/ - 删除业务线

    示例:
        >>> # 创建业务线
        >>> requests.post('/api/cmdb/business-lines/', data={'name': '电商平台'})
        >>> # 获取列表
        >>> requests.get('/api/cmdb/business-lines/')
    """

    queryset = BusinessLine.objects.all()
    serializer_class = BusinessLineSerializer


class EnvironmentViewSet(viewsets.ModelViewSet):
    """环境视图集.

    提供环境的完整 CRUD 操作。

    路由:
        GET /api/cmdb/environments/ - 获取环境列表
        POST /api/cmdb/environments/ - 创建新环境
        GET /api/cmdb/environments/{id}/ - 获取环境详情
        PUT /api/cmdb/environments/{id}/ - 更新环境
        DELETE /api/cmdb/environments/{id}/ - 删除环境

    列表默认按 sort_order 和 id 排序。
    """

    queryset = Environment.objects.all()
    serializer_class = EnvironmentSerializer


class ApplicationViewSet(viewsets.ModelViewSet):
    """应用视图集.

    提供应用的完整 CRUD 操作，支持按业务线筛选。

    路由:
        GET /api/cmdb/applications/ - 获取应用列表
        POST /api/cmdb/applications/ - 创建新应用
        GET /api/cmdb/applications/{id}/ - 获取应用详情
        PUT /api/cmdb/applications/{id}/ - 更新应用
        DELETE /api/cmdb/applications/{id}/ - 删除应用

    筛选参数:
        - business_line: 按业务线 ID 筛选

    示例:
        >>> # 获取所有应用
        >>> requests.get('/api/cmdb/applications/')
        >>> # 只获取某业务线的应用
        >>> requests.get('/api/cmdb/applications/?business_line=1')
    """

    queryset = Application.objects.select_related('business_line').all()
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        """获取查询集，支持按业务线筛选.

        从请求参数中获取 business_line ID 并过滤结果。

        Returns:
            过滤后的应用查询集。
        """
        queryset = super().get_queryset()
        business_line = self.request.query_params.get('business_line')
        if business_line:
            queryset = queryset.filter(business_line_id=business_line)
        return queryset


class ClusterViewSet(viewsets.ModelViewSet):
    """集群视图集.

    提供集群的完整 CRUD 操作，支持按应用和环境筛选。

    路由:
        GET /api/cmdb/clusters/ - 获取集群列表
        POST /api/cmdb/clusters/ - 创建新集群
        GET /api/cmdb/clusters/{id}/ - 获取集群详情
        PUT /api/cmdb/clusters/{id}/ - 更新集群
        DELETE /api/cmdb/clusters/{id}/ - 删除集群

    筛选参数:
        - application: 按应用 ID 筛选
        - environment: 按环境 ID 筛选

    示例:
        >>> # 获取所有集群
        >>> requests.get('/api/cmdb/clusters/')
        >>> # 只获取某应用的集群
        >>> requests.get('/api/cmdb/clusters/?application=1')
        >>> # 只获取某环境的集群
        >>> requests.get('/api/cmdb/clusters/?environment=2')
    """

    queryset = Cluster.objects.select_related('application', 'environment').all()
    serializer_class = ClusterSerializer

    def get_queryset(self):
        """获取查询集，支持按应用和环境筛选.

        从请求参数中获取 application 和 environment ID 并过滤结果。

        Returns:
            过滤后的集群查询集。
        """
        queryset = super().get_queryset()
        application = self.request.query_params.get('application')
        environment = self.request.query_params.get('environment')
        if application:
            queryset = queryset.filter(application_id=application)
        if environment:
            queryset = queryset.filter(environment_id=environment)
        return queryset


class TagViewSet(viewsets.ModelViewSet):
    """标签视图集.

    提供标签的完整 CRUD 操作。

    路由:
        GET /api/cmdb/tags/ - 获取标签列表
        POST /api/cmdb/tags/ - 创建新标签
        GET /api/cmdb/tags/{id}/ - 获取标签详情
        PUT /api/cmdb/tags/{id}/ - 更新标签
        DELETE /api/cmdb/tags/{id}/ - 删除标签

    注意:
        标签的 key-value 组合必须唯一，创建重复标签会返回错误。
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class HostViewSet(viewsets.ModelViewSet):
    """主机视图集.

    提供主机的完整 CRUD 操作，支持按业务线、集群、状态筛选。
    支持批量和单个主机标签更新。

    路由:
        GET /api/cmdb/hosts/ - 获取主机列表
        POST /api/cmdb/hosts/ - 创建新主机
        GET /api/cmdb/hosts/{id}/ - 获取主机详情
        PUT /api/cmdb/hosts/{id}/ - 更新主机
        DELETE /api/cmdb/hosts/{id}/ - 删除主机
        POST /api/cmdb/hosts/{id}/update_tags/ - 更新单个主机标签
        POST /api/cmdb/hosts/batch_update_tags/ - 批量更新主机标签

    筛选参数:
        - business_line: 按业务线 ID 筛选
        - cluster: 按集群 ID 筛选
        - status: 按状态筛选（online/offline/maintenance）

    附加动作:
        update_tags: 更新单个主机的标签
            方法: POST
            URL: /api/cmdb/hosts/{id}/update_tags/
            Body: {"tag_ids": [1, 2, 3]}
            返回: {"status": "ok"}

        batch_update_tags: 批量更新主机标签
            方法: POST
            URL: /api/cmdb/hosts/batch_update_tags/
            Body: {"host_ids": [1, 2, 3], "tag_ids": [4, 5]}
            返回: {"status": "ok"}

    示例:
        >>> # 获取所有主机
        >>> requests.get('/api/cmdb/hosts/')
        >>> # 获取某业务线的主机
        >>> requests.get('/api/cmdb/hosts/?business_line=1')
        >>> # 获取某集群的主机
        >>> requests.get('/api/cmdb/hosts/?cluster=1')
        >>> # 获取在线主机
        >>> requests.get('/api/cmdb/hosts/?status=online')
        >>> # 更新主机标签
        >>> requests.post('/api/cmdb/hosts/1/update_tags/', json={'tag_ids': [1, 2]})
    """

    queryset = Host.objects.select_related('business_line', 'cluster').prefetch_related('tags').all()
    serializer_class = HostSerializer

    def get_queryset(self):
        """获取查询集，支持按业务线、集群、状态筛选.

        从请求参数中获取筛选条件并过滤结果。

        Returns:
            过滤后的主机查询集。
        """
        queryset = super().get_queryset()
        business_line = self.request.query_params.get('business_line')
        cluster = self.request.query_params.get('cluster')
        status = self.request.query_params.get('status')
        if business_line:
            queryset = queryset.filter(business_line_id=business_line)
        if cluster:
            queryset = queryset.filter(cluster_id=cluster)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=True, methods=['post'])
    def update_tags(self, request, pk=None):
        """更新单个主机的标签.

        替换主机的所有标签为指定的标签列表。

        Args:
            request: HTTP 请求对象，包含 tag_ids 列表。
            pk: 主机的 ID。

        Returns:
            包含状态信息的响应。

        示例:
            POST /api/cmdb/hosts/1/update_tags/
            Body: {"tag_ids": [1, 2, 3]}
            Response: {"status": "ok"}
        """
        host = self.get_object()
        tag_ids = request.data.get('tag_ids', [])
        host.tags.set(tag_ids)
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'])
    def batch_update_tags(self, request):
        """批量更新多个主机的标签.

        为指定的所有主机设置相同的标签。

        Args:
            request: HTTP 请求对象，包含 host_ids 和 tag_ids 列表。

        Returns:
            包含状态信息的响应。

        示例:
            POST /api/cmdb/hosts/batch_update_tags/
            Body: {"host_ids": [1, 2, 3], "tag_ids": [4, 5]}
            Response: {"status": "ok"}
        """
        host_ids = request.data.get('host_ids', [])
        tag_ids = request.data.get('tag_ids', [])
        Host.objects.filter(id__in=host_ids).update(tags=tag_ids)
        return Response({'status': 'ok'})


class ApplicationDependencyViewSet(viewsets.ModelViewSet):
    """应用依赖关系视图集.

    提供应用依赖关系的完整 CRUD 操作。

    路由:
        GET /api/cmdb/application-dependencies/ - 获取依赖关系列表
        POST /api/cmdb/application-dependencies/ - 创建新依赖关系
        GET /api/cmdb/application-dependencies/{id}/ - 获取依赖关系详情
        PUT /api/cmdb/application-dependencies/{id}/ - 更新依赖关系
        DELETE /api/cmdb/application-dependencies/{id}/ - 删除依赖关系

    注意:
        同一应用不能重复依赖同一个应用，违反唯一约束会返回错误。

    示例:
        >>> # 创建依赖关系
        >>> requests.post('/api/cmdb/application-dependencies/', json={
        ...     'application': 1,
        ...     'depends_on': 2,
        ...     'description': '用户服务调用支付服务'
        ... })
    """

    queryset = ApplicationDependency.objects.select_related('application', 'depends_on').all()
    serializer_class = ApplicationDependencySerializer
