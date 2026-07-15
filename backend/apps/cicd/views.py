"""CI/CD 模块视图集.

提供 Jenkins 集成相关的 ViewSet，实现与 Jenkins 的交互功能。

主要功能:
    - Jenkins 实例管理（添加、编辑、删除 Jenkins 服务器）
    - Job 同步（从 Jenkins 实例拉取 Job 列表）
    - 构建触发（触发 Jenkins Job 构建）
    - 构建记录（查看历史构建记录）
    - 流水线部署（通过流水线触发部署任务）

典型使用场景:
    - 运维人员在平台上添加公司 Jenkins 服务器
    - 同步 Jenkins Job 到平台进行统一管理
    - 开发人员通过平台触发代码构建
    - 通过流水线一键部署应用到目标主机

API 路由:
    - /api/cicd/jenkins-instances/ - Jenkins 实例 CRUD
    - /api/cicd/jobs/ - Jenkins Job CRUD，build 动作触发构建
    - /api/cicd/builds/ - 构建记录（只读）
    - /api/cicd/pipelines/ - 流水线 CRUD，deploy 动作触发部署

错误处理:
    - Jenkins API 调用使用 try-except 包装，失败时返回友好错误信息
    - 超时时间设置为 10 秒
"""

import logging
from typing import Optional

import requests
from requests.auth import HTTPBasicAuth
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from .models import JenkinsInstance, JenkinsJob, BuildRecord, Pipeline
from .serializers import (
    JenkinsInstanceSerializer, JenkinsJobSerializer,
    BuildRecordSerializer, PipelineSerializer
)

# 模块级日志记录器
logger = logging.getLogger(__name__)


def get_jenkins_client(instance: JenkinsInstance) -> HTTPBasicAuth:
    """构建 Jenkins API 认证信息.

    Args:
        instance: Jenkins 实例对象，包含用户名和 API Token。

    Returns:
        HTTPBasicAuth 对象，用于 Jenkins API 认证。
    """
    return HTTPBasicAuth(instance.username, instance.api_token)


def sync_jenkins_jobs(instance: JenkinsInstance) -> None:
    """从 Jenkins 实例同步 Job 列表.

    调用 Jenkins API 获取所有 Job 信息，更新本地数据库。
    如果 Job 不存在则创建，存在则更新 URL。

    Args:
        instance: Jenkins 实例对象。

    Raises:
        requests.RequestException: Jenkins API 调用失败时记录日志但不抛出异常。
    """
    url = f"{instance.url}/api/json"
    try:
        response = requests.get(url, auth=get_jenkins_client(instance), timeout=10)
        if response.status_code == 200:
            data = response.json()
            for job_data in data.get('jobs', []):
                JenkinsJob.objects.update_or_create(
                    instance=instance,
                    name=job_data['name'],
                    defaults={'job_url': job_data.get('url', '')}
                )
            logger.info(f"成功同步 Jenkins 实例 {instance.name} 的 Job 列表")
        else:
            logger.warning(f"Jenkins 实例 {instance.name} API 返回状态码 {response.status_code}")
    except requests.RequestException as e:
        logger.error(f"同步 Jenkins 实例 {instance.name} 失败: {e}")


class JenkinsInstanceViewSet(viewsets.ModelViewSet):
    """Jenkins 实例视图集.

    管理 Jenkins 服务器实例，包括添加、编辑、删除、测试连接等功能。

    路由:
        GET /api/cicd/jenkins-instances/ - 获取实例列表
        POST /api/cicd/jenkins-instances/ - 创建新实例
        GET /api/cicd/jenkins-instances/{id}/ - 获取实例详情
        PUT /api/cicd/jenkins-instances/{id}/ - 更新实例
        DELETE /api/cicd/jenkins-instances/{id}/ - 删除实例
        POST /api/cicd/jenkins-instances/{id}/sync_jobs/ - 同步该实例的 Job 列表
    """

    queryset = JenkinsInstance.objects.all()
    serializer_class = JenkinsInstanceSerializer

    @action(detail=True, methods=['post'])
    def sync_jobs(self, request: Request, pk: Optional[str] = None) -> Response:
        """同步 Jenkins 实例的 Job 列表.

        从指定的 Jenkins 实例拉取所有 Job 信息并更新到本地数据库。

        Args:
            request: HTTP 请求对象。
            pk: Jenkins 实例的主键 ID。

        Returns:
            包含同步状态的响应对象。
        """
        instance = self.get_object()
        sync_jenkins_jobs(instance)
        return Response({'status': 'synced'})


class JenkinsJobViewSet(viewsets.ModelViewSet):
    """Jenkins Job 视图集.

    管理 Jenkins Job，包括查看、同步、触发构建等操作。

    路由:
        GET /api/cicd/jobs/ - 获取 Job 列表
        POST /api/cicd/jobs/ - 创建新 Job（较少使用）
        GET /api/cicd/jobs/{id}/ - 获取 Job 详情
        PUT /api/cicd/jobs/{id}/ - 更新 Job
        DELETE /api/cicd/jobs/{id}/ - 删除 Job
        POST /api/cicd/jobs/{id}/build/ - 触发构建
        GET /api/cicd/jobs/{id}/builds/ - 获取该 Job 的构建历史
        POST /api/cicd/jobs/{id}/refresh_status/ - 刷新 Job 状态
    """

    queryset = JenkinsJob.objects.select_related('instance').all()
    serializer_class = JenkinsJobSerializer

    @action(detail=True, methods=['post'])
    def build(self, request: Request, pk: Optional[str] = None) -> Response:
        """触发 Jenkins Job 构建.

        调用 Jenkins API 触发指定 Job 的构建，并创建本地构建记录。

        Args:
            request: HTTP 请求对象，包含当前用户信息。
            pk: Jenkins Job 的主键 ID。

        Returns:
            成功时返回构建状态和新构建号，失败时返回错误信息。
        """
        job = self.get_object()
        url = f"{job.instance.url}/job/{job.name}/build"
        try:
            response = requests.post(
                url,
                auth=get_jenkins_client(job.instance),
                timeout=10
            )
            if response.status_code in [200, 201]:
                # 创建构建记录
                last_build = job.builds.order_by('-build_number').first()
                new_build_number = (last_build.build_number + 1) if last_build else 1
                BuildRecord.objects.create(
                    job=job,
                    build_number=new_build_number,
                    status='pending',
                    executor=request.user.username
                )
                logger.info(f"用户 {request.user.username} 触发了 Job {job.name} 的构建")
                return Response({'status': 'triggered', 'build_number': new_build_number})
            return Response({'error': 'Trigger failed'}, status=400)
        except requests.RequestException as e:
            logger.error(f"触发 Job {job.name} 构建失败: {e}")
            return Response({'error': f'构建触发失败: {str(e)}'}, status=500)

    @action(detail=True, methods=['get'])
    def builds(self, request: Request, pk: Optional[str] = None) -> Response:
        """获取 Jenkins Job 的构建历史.

        返回该 Job 最近 50 条构建记录。

        Args:
            request: HTTP 请求对象。
            pk: Jenkins Job 的主键 ID。

        Returns:
            包含构建记录列表的响应对象。
        """
        job = self.get_object()
        records = job.builds.all()[:50]
        serializer = BuildRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def refresh_status(self, request: Request, pk: Optional[str] = None) -> Response:
        """刷新 Jenkins Job 的最新构建状态.

        调用 Jenkins API 获取 Job 的最后一次构建信息并更新本地记录。

        Args:
            request: HTTP 请求对象。
            pk: Jenkins Job 的主键 ID。

        Returns:
            包含刷新状态的响应对象。
        """
        job = self.get_object()
        url = f"{job.instance.url}/job/{job.name}/lastBuild/api/json"
        try:
            response = requests.get(url, auth=get_jenkins_client(job.instance), timeout=10)
            if response.status_code == 200:
                data = response.json()
                job.last_build_number = data.get('number', 0)
                job.last_build_status = data.get('result') or 'running'
                job.save()
                logger.debug(f"刷新 Job {job.name} 状态成功")
            return Response({'status': 'refreshed'})
        except requests.RequestException as e:
            logger.error(f"刷新 Job {job.name} 状态失败: {e}")
            return Response({'status': 'refreshed', 'warning': '状态可能不是最新'})


class BuildRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """构建记录视图集.

    提供构建记录的只读访问，按构建时间倒序排列。

    路由:
        GET /api/cicd/builds/ - 获取构建记录列表
        GET /api/cicd/builds/{id}/ - 获取构建记录详情
    """

    queryset = BuildRecord.objects.select_related('job', 'job__instance').all()
    serializer_class = BuildRecordSerializer


class PipelineViewSet(viewsets.ModelViewSet):
    """流水线视图集.

    管理部署流水线，关联 Jenkins Job 和目标主机，支持一键部署。

    路由:
        GET /api/cicd/pipelines/ - 获取流水线列表
        POST /api/cicd/pipelines/ - 创建新流水线
        GET /api/cicd/pipelines/{id}/ - 获取流水线详情
        PUT /api/cicd/pipelines/{id}/ - 更新流水线
        DELETE /api/cicd/pipelines/{id}/ - 删除流水线
        POST /api/cicd/pipelines/{id}/deploy/ - 触发流水线部署
    """

    queryset = Pipeline.objects.select_related('job').prefetch_related('target_hosts').all()
    serializer_class = PipelineSerializer

    @action(detail=True, methods=['post'])
    def deploy(self, request: Request, pk: Optional[str] = None) -> Response:
        """触发流水线部署任务.

        根据流水线配置，调用 Jenkins API 触发关联的 Job 构建。

        Args:
            request: HTTP 请求对象，包含当前用户信息。
            pk: 流水线的主键 ID。

        Returns:
            包含部署状态的响应对象。
        """
        pipeline = self.get_object()
        url = f"{pipeline.job.instance.url}/job/{pipeline.job.name}/build"
        try:
            response = requests.post(
                url,
                auth=get_jenkins_client(pipeline.job.instance),
                timeout=10
            )
            logger.info(
                f"用户 {request.user.username} 触发了流水线 {pipeline.name} 的部署，"
                f"目标主机: {[h.hostname for h in pipeline.target_hosts.all()]}"
            )
            return Response({'status': 'deploy triggered'})
        except requests.RequestException as e:
            logger.error(f"触发流水线 {pipeline.name} 部署失败: {e}")
            return Response({'error': f'部署触发失败: {str(e)}'}, status=500)
