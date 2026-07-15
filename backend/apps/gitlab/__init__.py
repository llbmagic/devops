"""GitLab 集成模块.

提供 GitLab 代码仓库和 Merge Request 的管理功能，支持:
    - GitLab 实例管理（支持多个 GitLab 实例）
    - 项目同步（从 GitLab 实例拉取项目列表）
    - MR 状态查询（查看 MR 的审批状态和讨论）
    - CI 流水线触发（通过 GitLab CI API 触发流水线）

典型使用场景:
    - 运维人员添加公司 GitLab 服务器
    - 同步项目列表到平台统一管理
    - 查看 MR 审批状态和 CI 流水线结果
    - 触发 GitLab CI 流水线执行

数据模型层次结构:
    GitLabInstance (GitLab 服务器)
        └── Project (代码仓库)
              └── MergeRequest (合并请求)

模块导出:
    - GitLabInstance: GitLab 实例模型
    - Project: 代码仓库模型
    - MergeRequest: 合并请求模型

示例:
    >>> from apps.gitlab.models import GitLabInstance, Project
    >>> instance = GitLabInstance.objects.create(
    ...     name='公司 GitLab',
    ...     url='https://gitlab.example.com',
    ...     access_token='your-token'
    ... )
"""

__all__ = ['GitLabInstance', 'Project', 'MergeRequest']
