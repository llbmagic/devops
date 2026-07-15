"""GitLab 模块视图集.

提供 GitLab 集成的 ViewSet，实现与 GitLab API 的交互功能。

主要功能:
    - GitLab 实例管理（添加、编辑、删除）
    - 项目同步（从 GitLab 实例拉取项目列表）
    - MR 列表（查看 MR 状态，支持按项目筛选）
    - MR 详情（查看 MR 详细信息）
    - 触发 CI 流水线

API 路由:
    - /api/gitlab/instances/ - GitLab 实例 CRUD
    - /api/gitlab/instances/{id}/sync_projects/ - 同步项目列表
    - /api/gitlab/instances/{id}/test_connection/ - 测试连接
    - /api/gitlab/projects/ - 项目列表
    - /api/gitlab/merge-requests/ - MR 列表
    - /api/gitlab/merge-requests/{id}/refresh/ - 刷新 MR 状态
    - /api/gitlab/projects/{id}/trigger_pipeline/ - 触发流水线

认证说明:
    所有视图集默认要求登录认证（IsAuthenticated）。
"""

import logging
from typing import Optional

import requests
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from .models import GitLabInstance, Project, MergeRequest
from .serializers import (
    GitLabInstanceSerializer, ProjectSerializer, MergeRequestSerializer
)

logger = logging.getLogger(__name__)


def get_gitlab_headers(instance: GitLabInstance) -> dict:
    """构建 GitLab API 请求头.

    Args:
        instance: GitLab 实例对象。

    Returns:
        包含认证信息的请求头字典。
    """
    return {
        'PRIVATE-TOKEN': instance.access_token,
        'Content-Type': 'application/json'
    }


def sync_gitlab_projects(instance: GitLabInstance) -> None:
    """从 GitLab 实例同步项目列表.

    调用 GitLab API 获取该实例下所有可访问的项目，
    并更新或创建本地 Project 记录。

    Args:
        instance: GitLab 实例对象。

    示例:
        >>> instance = GitLabInstance.objects.get(id=1)
        >>> sync_gitlab_projects(instance)
    """
    url = f"{instance.url}/api/v4/projects"
    params = {
        'membership': True,
        'per_page': 100,
        'order_by': 'last_activity_at',
        'sort': 'desc'
    }
    try:
        response = requests.get(
            url,
            headers=get_gitlab_headers(instance),
            params=params,
            timeout=30
        )
        if response.status_code == 200:
            projects = response.json()
            for p in projects:
                Project.objects.update_or_create(
                    instance=instance,
                    gitlab_id=p['id'],
                    defaults={
                        'name': p['name'],
                        'path_with_namespace': p['path_with_namespace'],
                        'web_url': p['web_url'],
                        'default_branch': p.get('default_branch', 'main'),
                        'last_activity_at': p.get('last_activity_at')
                    }
                )
            logger.info(f"成功同步 GitLab 实例 {instance.name} 的项目列表")
        else:
            logger.warning(
                f"GitLab 实例 {instance.name} API 返回状态码 {response.status_code}"
            )
    except requests.RequestException as e:
        logger.error(f"同步 GitLab 项目失败: {e}")


class GitLabInstanceViewSet(viewsets.ModelViewSet):
    """GitLab 实例视图集.

    提供 GitLab 实例的完整 CRUD 操作，支持同步项目和测试连接。

    路由:
        GET /api/gitlab/instances/ - 获取实例列表
        POST /api/gitlab/instances/ - 创建新实例
        GET /api/gitlab/instances/{id}/ - 获取实例详情
        PUT /api/gitlab/instances/{id}/ - 更新实例
        DELETE /api/gitlab/instances/{id}/ - 删除实例
        POST /api/gitlab/instances/{id}/sync_projects/ - 同步项目列表
        POST /api/gitlab/instances/{id}/test_connection/ - 测试连接

    示例:
        >>> # 创建实例
        >>> requests.post('/api/gitlab/instances/', json={
        ...     'name': '公司 GitLab',
        ...     'url': 'https://gitlab.example.com',
        ...     'access_token': 'glpat-xxxxx'
        ... })
        >>> # 同步项目
        >>> requests.post('/api/gitlab/instances/1/sync_projects/')
    """

    queryset = GitLabInstance.objects.all()
    serializer_class = GitLabInstanceSerializer

    @action(detail=True, methods=['post'])
    def sync_projects(self, request: Request, pk: Optional[str] = None) -> Response:
        """同步该实例的项目列表.

        从 GitLab API 获取项目列表并更新本地数据库。

        Returns:
            包含同步状态的响应。

        示例:
            POST /api/gitlab/instances/1/sync_projects/
            Response: {'status': 'synced'}
        """
        instance = self.get_object()
        sync_gitlab_projects(instance)
        return Response({'status': 'synced'})

    @action(detail=True, methods=['post'])
    def test_connection(self, request: Request, pk: Optional[str] = None) -> Response:
        """测试 GitLab 连接.

        调用 GitLab API 获取当前用户信息验证连接是否正常。

        Returns:
            包含连接测试结果的响应。

        示例:
            POST /api/gitlab/instances/1/test_connection/
            Response: {'status': 'ok', 'user': 'gitlab-user'}
        """
        instance = self.get_object()
        try:
            response = requests.get(
                f"{instance.url}/api/v4/user",
                headers=get_gitlab_headers(instance),
                timeout=10
            )
            if response.status_code == 200:
                return Response({
                    'status': 'ok',
                    'user': response.json().get('username')
                })
            return Response({'error': '连接失败'}, status=400)
        except requests.RequestException as e:
            logger.error(f"测试 GitLab 连接失败: {e}")
            return Response({'error': str(e)}, status=500)


class ProjectViewSet(viewsets.ModelViewSet):
    """代码仓库视图集.

    提供项目的完整 CRUD 操作，支持按实例筛选。

    路由:
        GET /api/gitlab/projects/ - 获取项目列表
        POST /api/gitlab/projects/ - 创建新项目（仅本地记录）
        GET /api/gitlab/projects/{id}/ - 获取项目详情
        PUT /api/gitlab/projects/{id}/ - 更新项目
        DELETE /api/gitlab/projects/{id}/ - 删除项目
        POST /api/gitlab/projects/{id}/trigger_pipeline/ - 触发流水线

    筛选参数:
        - instance: 按实例 ID 筛选

    示例:
        >>> requests.get('/api/gitlab/projects/?instance=1')
        >>> requests.post('/api/gitlab/projects/1/trigger_pipeline/', json={'ref': 'main'})
    """

    queryset = Project.objects.select_related('instance').all()
    serializer_class = ProjectSerializer

    def get_queryset(self):
        """获取查询集，支持按实例筛选.

        从请求参数中获取 instance ID 并过滤结果。

        Returns:
            过滤后的项目查询集。
        """
        queryset = super().get_queryset()
        instance_id = self.request.query_params.get('instance')
        if instance_id:
            queryset = queryset.filter(instance_id=instance_id)
        return queryset

    @action(detail=True, methods=['post'])
    def trigger_pipeline(self, request: Request, pk: Optional[str] = None) -> Response:
        """触发 GitLab CI 流水线.

        在指定分支上触发流水线执行。

        Args:
            request: 包含 ref（分支名）参数，默认为项目默认分支。

        Returns:
            包含流水线创建结果的响应。

        示例:
            POST /api/gitlab/projects/1/trigger_pipeline/
            Body: {'ref': 'main'}
            Response: {'status': 'created', 'pipeline_id': 123, 'web_url': '...'}
        """
        project = self.get_object()
        ref = request.data.get('ref', project.default_branch)
        try:
            response = requests.post(
                f"{project.instance.url}/api/v4/projects/{project.gitlab_id}/pipeline",
                headers=get_gitlab_headers(project.instance),
                json={'ref': ref},
                timeout=10
            )
            if response.status_code == 201:
                pipeline = response.json()
                logger.info(
                    f"触发项目 {project.name} 流水线成功，Pipeline ID: {pipeline['id']}"
                )
                return Response({
                    'status': 'created',
                    'pipeline_id': pipeline['id'],
                    'web_url': pipeline['web_url']
                })
            logger.warning(f"创建流水线失败，状态码: {response.status_code}")
            return Response({'error': '创建流水线失败'}, status=400)
        except requests.RequestException as e:
            logger.error(f"触发流水线失败: {e}")
            return Response({'error': str(e)}, status=500)


class MergeRequestViewSet(viewsets.ModelViewSet):
    """合并请求视图集.

    提供 MR 的完整 CRUD 操作，支持按项目和状态筛选。

    路由:
        GET /api/gitlab/merge-requests/ - 获取 MR 列表
        POST /api/gitlab/merge-requests/ - 创建 MR（仅本地记录）
        GET /api/gitlab/merge-requests/{id}/ - 获取 MR 详情
        PUT /api/gitlab/merge-requests/{id}/ - 更新 MR
        DELETE /api/gitlab/merge-requests/{id}/ - 删除 MR
        POST /api/gitlab/merge-requests/{id}/refresh/ - 刷新 MR 状态

    筛选参数:
        - project: 按项目 ID 筛选
        - state: 按状态筛选（opened/closed/merged）

    示例:
        >>> requests.get('/api/gitlab/merge-requests/?project=1')
        >>> requests.get('/api/gitlab/merge-requests/?state=opened')
        >>> requests.post('/api/gitlab/merge-requests/1/refresh/')
    """

    queryset = MergeRequest.objects.select_related(
        'project', 'project__instance'
    ).all()
    serializer_class = MergeRequestSerializer

    def get_queryset(self):
        """获取查询集，支持按项目和状态筛选.

        从请求参数中获取筛选条件并过滤结果。

        Returns:
            过滤后的 MR 查询集。
        """
        queryset = super().get_queryset()
        project_id = self.request.query_params.get('project')
        state = self.request.query_params.get('state')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        if state:
            queryset = queryset.filter(state=state)
        return queryset

    @action(detail=True, methods=['post'])
    def refresh(self, request: Request, pk: Optional[str] = None) -> Response:
        """刷新 MR 状态.

        从 GitLab API 获取最新状态并更新本地记录。

        Returns:
            包含刷新结果的响应。

        示例:
            POST /api/gitlab/merge-requests/1/refresh/
            Response: {'status': 'refreshed'}
        """
        mr = self.get_object()
        try:
            response = requests.get(
                f"{mr.project.instance.url}/api/v4/projects/{mr.project.gitlab_id}/merge_requests/{mr.gitlab_id}",
                headers=get_gitlab_headers(mr.project.instance),
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                mr.state = data['state']
                mr.title = data['title']
                mr.review_status = 'approved' if data.get('approved', False) else 'pending'
                if data.get('pipeline'):
                    mr.pipeline_status = data['pipeline'].get('status')
                mr.save()
                logger.info(f"刷新 MR !{mr.gitlab_id} 状态成功")
            return Response({'status': 'refreshed'})
        except requests.RequestException as e:
            logger.error(f"刷新 MR 状态失败: {e}")
            return Response({'status': 'refreshed', 'warning': str(e)})
