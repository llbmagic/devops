import requests
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import JenkinsInstance, JenkinsJob, BuildRecord, Pipeline
from .serializers import (
    JenkinsInstanceSerializer, JenkinsJobSerializer,
    BuildRecordSerializer, PipelineSerializer
)


def get_jenkins_client(instance):
    """构建 Jenkins API 请求头"""
    from requests.auth import HTTPBasicAuth
    return HTTPBasicAuth(instance.username, instance.api_token)


def sync_jenkins_jobs(instance):
    """从 Jenkins 同步 Job 列表"""
    url = f"{instance.url}/api/json"
    response = requests.get(url, auth=get_jenkins_client(instance), timeout=10)
    if response.status_code == 200:
        data = response.json()
        for job_data in data.get('jobs', []):
            JenkinsJob.objects.update_or_create(
                instance=instance,
                name=job_data['name'],
                defaults={'job_url': job_data.get('url', '')}
            )


class JenkinsInstanceViewSet(viewsets.ModelViewSet):
    queryset = JenkinsInstance.objects.all()
    serializer_class = JenkinsInstanceSerializer

    @action(detail=True, methods=['post'])
    def sync_jobs(self, request, pk=None):
        instance = self.get_object()
        sync_jenkins_jobs(instance)
        return Response({'status': 'synced'})


class JenkinsJobViewSet(viewsets.ModelViewSet):
    queryset = JenkinsJob.objects.select_related('instance').all()
    serializer_class = JenkinsJobSerializer

    @action(detail=True, methods=['post'])
    def build(self, request, pk=None):
        """触发 Jenkins 构建"""
        job = self.get_object()
        url = f"{job.instance.url}/job/{job.name}/build"
        response = requests.post(url, auth=get_jenkins_client(job.instance), timeout=10)
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
            return Response({'status': 'triggered', 'build_number': new_build_number})
        return Response({'error': 'Trigger failed'}, status=400)

    @action(detail=True, methods=['get'])
    def builds(self, request, pk=None):
        job = self.get_object()
        records = job.builds.all()[:50]
        serializer = BuildRecordSerializer(records, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def refresh_status(self, request, pk=None):
        """刷新 Job 状态"""
        job = self.get_object()
        url = f"{job.instance.url}/job/{job.name}/lastBuild/api/json"
        response = requests.get(url, auth=get_jenkins_client(job.instance), timeout=10)
        if response.status_code == 200:
            data = response.json()
            job.last_build_number = data.get('number', 0)
            job.last_build_status = data.get('result') or 'running'
            job.save()
        return Response({'status': 'refreshed'})


class BuildRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = BuildRecord.objects.select_related('job', 'job__instance').all()
    serializer_class = BuildRecordSerializer


class PipelineViewSet(viewsets.ModelViewSet):
    queryset = Pipeline.objects.select_related('job').prefetch_related('target_hosts').all()
    serializer_class = PipelineSerializer

    @action(detail=True, methods=['post'])
    def deploy(self, request, pk=None):
        """发起部署任务"""
        pipeline = self.get_object()
        # 触发关联的 Jenkins Job
        url = f"{pipeline.job.instance.url}/job/{pipeline.job.name}/build"
        requests.post(url, auth=get_jenkins_client(pipeline.job.instance), timeout=10)
        return Response({'status': 'deploy triggered'})
