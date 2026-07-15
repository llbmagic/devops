"""Ansible 模块视图集.

提供 Ansible 集成相关的 ViewSet。

API 路由:
    - /api/ansible/servers/ - Ansible 控制节点 CRUD
    - /api/ansible/servers/{id}/test_connection/ - 测试连接
    - /api/ansible/playbooks/ - 剧本 CRUD
    - /api/ansible/playbooks/{id}/run/ - 执行剧本
    - /api/ansible/records/ - 执行记录列表（只读）
"""

import logging
import subprocess
from typing import Optional

from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from .models import AnsibleServer, Playbook, TaskRecord
from .serializers import (
    AnsibleServerSerializer, PlaybookSerializer, TaskRecordSerializer
)

logger = logging.getLogger(__name__)


def build_ansible_command(
    server: AnsibleServer,
    playbook: Playbook,
    target_hosts: str,
    extra_vars: Optional[str] = None
) -> list:
    """构建 ansible-playbook 命令.

    Args:
        server: Ansible 控制节点。
        playbook: 要执行的剧本。
        target_hosts: 目标主机。
        extra_vars: 额外变量。

    Returns:
        命令列表。
    """
    ssh_cmd = [
        'ssh',
        '-o', 'StrictHostKeyChecking=no',
        '-o', 'UserKnownHostsFile=/dev/null',
        '-p', str(server.ssh_port),
    ]
    if server.private_key_path:
        ssh_cmd.extend(['-i', server.private_key_path])
    ssh_cmd.append(f'{server.ssh_user}@{server.host}')

    playbook_cmd = [
        'ansible-playbook',
        playbook.playbook_path,
        '-h', target_hosts,
    ]
    if extra_vars:
        playbook_cmd.extend(['-e', extra_vars])

    return ssh_cmd + ['--'] + playbook_cmd


class AnsibleServerViewSet(viewsets.ModelViewSet):
    """Ansible 控制节点视图集.

    提供控制节点的完整 CRUD 操作，支持测试连接。

    路由:
        GET /api/ansible/servers/ - 获取节点列表
        POST /api/ansible/servers/ - 创建节点
        GET /api/ansible/servers/{id}/ - 获取节点详情
        PUT /api/ansible/servers/{id}/ - 更新节点
        DELETE /api/ansible/servers/{id}/ - 删除节点
        POST /api/ansible/servers/{id}/test_connection/ - 测试连接

    示例:
        >>> requests.post('/api/ansible/servers/', json={
        ...     'name': 'Ansible Controller',
        ...     'host': '192.168.1.100',
        ...     'ssh_user': 'root'
        ... })
        >>> requests.post('/api/ansible/servers/1/test_connection/')
    """

    queryset = AnsibleServer.objects.all()
    serializer_class = AnsibleServerSerializer

    @action(detail=True, methods=['post'])
    def test_connection(self, request: Request, pk: Optional[str] = None) -> Response:
        """测试 Ansible 控制节点连接.

        通过 SSH 连接测试验证控制节点是否可达。

        Returns:
            包含连接测试结果的响应。

        示例:
            POST /api/ansible/servers/1/test_connection/
            Response: {'status': 'ok'}
        """
        server = self.get_object()
        try:
            ssh_cmd = ['ssh', '-o', 'ConnectTimeout=5', '-o', 'StrictHostKeyChecking=no']
            if server.private_key_path:
                ssh_cmd.extend(['-i', server.private_key_path])
            ssh_cmd.extend([
                '-p', str(server.ssh_port),
                f'{server.ssh_user}@{server.host}',
                'echo', 'ok'
            ])
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0:
                return Response({'status': 'ok'})
            logger.warning(f"SSH 连接失败，返回码: {result.returncode}")
            return Response({'error': '连接失败'}, status=400)
        except subprocess.TimeoutExpired:
            return Response({'error': '连接超时'}, status=400)
        except Exception as e:
            logger.error(f"测试连接异常: {e}")
            return Response({'error': str(e)}, status=500)


class PlaybookViewSet(viewsets.ModelViewSet):
    """剧本视图集.

    提供剧本的完整 CRUD 操作，支持执行剧本。

    路由:
        GET /api/ansible/playbooks/ - 获取剧本列表
        POST /api/ansible/playbooks/ - 创建剧本
        GET /api/ansible/playbooks/{id}/ - 获取剧本详情
        PUT /api/ansible/playbooks/{id}/ - 更新剧本
        DELETE /api/ansible/playbooks/{id}/ - 删除剧本
        POST /api/ansible/playbooks/{id}/run/ - 执行剧本

    示例:
        >>> requests.post('/api/ansible/playbooks/', json={
        ...     'name': '部署 Web',
        ...     'playbook_path': '/opt/ansible/deploy-web.yml'
        ... })
        >>> requests.post('/api/ansible/playbooks/1/run/', json={
        ...     'target_hosts': 'web-01,web-02'
        ... })
    """

    queryset = Playbook.objects.select_related('created_by').all()
    serializer_class = PlaybookSerializer

    def perform_create(self, serializer):
        """创建时自动设置创建人."""
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def run(self, request: Request, pk: Optional[str] = None) -> Response:
        """执行 Ansible 剧本.

        使用第一个可用的控制节点执行 ansible-playbook 命令。

        Args:
            request: 包含 target_hosts 和 variables 参数。

        Returns:
            包含执行结果的响应。

        示例:
            POST /api/ansible/playbooks/1/run/
            Body: {'target_hosts': 'all', 'variables': 'env: prod'}
            Response: {'status': 'success', 'record_id': 1, 'output': '...'}
        """
        playbook = self.get_object()
        target_hosts = request.data.get('target_hosts', 'all')
        variables = request.data.get('variables', playbook.variables)

        server = AnsibleServer.objects.filter(is_active=True).first()
        if not server:
            return Response({'error': '没有可用的 Ansible 控制节点'}, status=400)

        record = TaskRecord.objects.create(
            playbook=playbook,
            server=server,
            target_hosts=target_hosts,
            variables=variables,
            status='running',
            executor=request.user.username
        )

        try:
            cmd = build_ansible_command(server, playbook, target_hosts, variables)
            result = subprocess.run(
                ' '.join(cmd),
                shell=True,
                capture_output=True,
                text=True,
                timeout=3600
            )

            record.output = result.stdout[-10*1024*1024:]
            if result.returncode == 0:
                record.status = 'success'
            else:
                record.status = 'failed'
                record.error = result.stderr[-10*1024*1024:]
            record.finished_at = timezone.now()

            logger.info(
                f"用户 {request.user.username} 执行剧本 {playbook.name} "
                f"到主机 {target_hosts}，状态: {record.status}"
            )
        except subprocess.TimeoutExpired:
            record.status = 'failed'
            record.error = '执行超时（超过1小时）'
            record.finished_at = timezone.now()
        except Exception as e:
            record.status = 'failed'
            record.error = str(e)
            record.finished_at = timezone.now()
            logger.error(f"执行剧本失败: {e}")
        finally:
            record.save()

        return Response({
            'status': record.status,
            'record_id': record.id,
            'output': record.output[-5000:] if record.output else None
        })


class TaskRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """任务执行记录视图集（只读）.

    提供执行记录的查询功能，支持按剧本和状态筛选。

    路由:
        GET /api/ansible/records/ - 获取执行记录列表
        GET /api/ansible/records/{id}/ - 获取执行记录详情

    筛选参数:
        - playbook: 按剧本 ID 筛选
        - status: 按状态筛选（pending/running/success/failed）

    示例:
        >>> requests.get('/api/ansible/records/')
        >>> requests.get('/api/ansible/records/?playbook=1')
        >>> requests.get('/api/ansible/records/?status=failed')
    """

    queryset = TaskRecord.objects.select_related(
        'playbook', 'server'
    ).all()
    serializer_class = TaskRecordSerializer

    def get_queryset(self):
        """获取查询集，支持按剧本和状态筛选."""
        queryset = super().get_queryset()
        playbook_id = self.request.query_params.get('playbook')
        status = self.request.query_params.get('status')
        if playbook_id:
            queryset = queryset.filter(playbook_id=playbook_id)
        if status:
            queryset = queryset.filter(status=status)
        return queryset
