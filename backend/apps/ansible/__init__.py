"""Ansible 集成模块.

提供 Ansible 自动化执行的功能，支持:
    - Ansible 控制节点管理
    - 剧本（Playbook）定义和管理
    - 批量任务执行
    - 执行结果记录和追溯

典型使用场景:
    - 运维人员配置 Ansible 控制节点
    - 创建和管理常用的运维剧本
    - 批量执行任务到目标主机
    - 查看历史执行记录和输出

数据模型层次结构:
    AnsibleServer (Ansible 控制节点)
        └── Playbook (剧本)
              └── TaskRecord (执行记录)

模块导出:
    - AnsibleServer: Ansible 控制节点模型
    - Playbook: 剧本模型
    - TaskRecord: 执行记录模型

示例:
    >>> from apps.ansible.models import AnsibleServer, Playbook
    >>> server = AnsibleServer.objects.create(
    ...     name='Ansible Controller',
    ...     host='192.168.1.100',
    ...     ssh_user='root'
    ... )
"""

__all__ = ['AnsibleServer', 'Playbook', 'TaskRecord']
