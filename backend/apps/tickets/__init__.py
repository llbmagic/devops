"""工单审批模块.

提供工单创建和审批流程管理的功能，支持:
    - 工单模板定义（定义不同类型的工单及其审批流程）
    - 工单实例创建和审批
    - 多级审批流程支持
    - 状态流转管理

典型使用场景:
    - 用户提交服务器申请工单
    - 运维人员审批工单
    - 管理员配置工单模板和审批流程

状态流转:
    draft -> pending -> approved/rejected -> closed

数据模型层次结构:
    TicketTemplate (工单模板)
        └── Ticket (工单实例)
              └── ApprovalStep (审批步骤)
                    └── ApprovalRecord (审批记录)

模块导出:
    - TicketTemplate: 工单模板模型
    - Ticket: 工单模型
    - ApprovalStep: 审批步骤模型
    - ApprovalRecord: 审批记录模型

示例:
    >>> from apps.tickets.models import TicketTemplate, Ticket
    >>> template = TicketTemplate.objects.create(
    ...     name='服务器申请',
    ...     code='server_request',
    ...     approvers='admin,manager'
    ... )
"""

__all__ = ['TicketTemplate', 'Ticket', 'ApprovalStep', 'ApprovalRecord']
