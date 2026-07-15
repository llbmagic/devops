"""CI/CD 模块.

提供 Jenkins 集成相关的功能，包括 Jenkins 实例管理、Job 同步、构建触发、
构建记录查看和流水线部署等。

公开子模块:
    - models: JenkinsInstance, JenkinsJob, BuildRecord, Pipeline
    - serializers: 各模型的序列化器
    - views: REST API 视图集
    - urls: 路由配置

典型使用场景:
    - 运维人员在平台上添加公司 Jenkins 服务器
    - 同步 Jenkins Job 到平台进行统一管理
    - 开发人员通过平台触发代码构建
    - 通过流水线一键部署应用到目标主机

示例:
    >>> from apps.cicd.models import JenkinsInstance, JenkinsJob
    >>> instance = JenkinsInstance.objects.create(name='Jenkins主服务器', url='http://jenkins.example.com')
"""

# 显式导出公开子模块（延迟导入，避免 AppRegistryNotReady）
__all__ = [
    'JenkinsInstance',
    'JenkinsJob',
    'BuildRecord',
    'Pipeline',
    'JenkinsInstanceSerializer',
    'JenkinsJobSerializer',
    'BuildRecordSerializer',
    'PipelineSerializer',
    'JenkinsInstanceViewSet',
    'JenkinsJobViewSet',
    'BuildRecordViewSet',
    'PipelineViewSet',
]
