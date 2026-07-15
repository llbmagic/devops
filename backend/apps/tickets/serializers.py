"""工单审批模块序列化器.

提供工单模板、工单、审批步骤、审批记录的序列化器。
"""

from rest_framework import serializers
from .models import TicketTemplate, Ticket, ApprovalStep, ApprovalRecord


class TicketTemplateSerializer(serializers.ModelSerializer):
    """工单模板序列化器.

    用于序列化工单模板模型。

    新增字段:
        ticket_count: 使用该模板的工单数量（只读）。

    示例:
        >>> serializer = TicketTemplateSerializer(template)
        >>> serializer.data
        {'id': 1, 'name': '服务器申请', 'code': 'server_request', 'ticket_count': 5, ...}
    """

    ticket_count = serializers.SerializerMethodField(
        help_text='使用该模板的工单数量'
    )

    class Meta:
        """序列化器元数据."""
        model = TicketTemplate
        fields = '__all__'
        read_only_fields = ['id', 'created_at']

    def get_ticket_count(self, obj: TicketTemplate) -> int:
        """获取使用该模板的工单数量."""
        return obj.ticket_set.count()


class ApprovalRecordSerializer(serializers.ModelSerializer):
    """审批记录序列化器.

    用于序列化审批记录模型。

    新增字段:
        operator_name: 操作人用户名（只读）。
        action_display: 操作描述（只读）。

    示例:
        >>> serializer = ApprovalRecordSerializer(record)
        >>> serializer.data
        {'id': 1, 'operator_name': 'admin', 'action_display': '批准', ...}
    """

    operator_name = serializers.CharField(
        source='operator.username',
        read_only=True,
        help_text='操作人用户名'
    )
    action_display = serializers.CharField(
        source='get_action_display',
        read_only=True,
        help_text='操作描述'
    )

    class Meta:
        """序列化器元数据."""
        model = ApprovalRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ApprovalStepSerializer(serializers.ModelSerializer):
    """审批步骤序列化器.

    用于序列化审批步骤模型。

    新增字段:
        approver_name: 审批人用户名（只读）。
        status_display: 状态描述（只读）。
        records: 审批记录列表（只读）。

    示例:
        >>> serializer = ApprovalStepSerializer(step)
        >>> serializer.data
        {'id': 1, 'step': 0, 'approver_name': 'admin', 'status_display': '待审批', ...}
    """

    approver_name = serializers.CharField(
        source='approver.username',
        read_only=True,
        help_text='审批人用户名'
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
        help_text='状态描述'
    )
    records = ApprovalRecordSerializer(many=True, read_only=True)

    class Meta:
        """序列化器元数据."""
        model = ApprovalStep
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class TicketSerializer(serializers.ModelSerializer):
    """工单序列化器.

    用于序列化工单模型，包含完整的审批步骤信息。

    新增字段:
        template_name: 模板名称（只读）。
        applicant_name: 申请人用户名（只读）。
        status_display: 状态描述（只读）。
        approval_steps: 审批步骤列表（只读）。

    示例:
        >>> serializer = TicketSerializer(ticket)
        >>> serializer.data
        {'id': 1, 'title': '申请服务器', 'template_name': '服务器申请',
         'applicant_name': 'user1', 'status_display': '待审批', ...}
    """

    template_name = serializers.CharField(
        source='template.name',
        read_only=True,
        help_text='模板名称'
    )
    applicant_name = serializers.CharField(
        source='applicant.username',
        read_only=True,
        help_text='申请人用户名'
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
        help_text='状态描述'
    )
    approval_steps = ApprovalStepSerializer(many=True, read_only=True)

    class Meta:
        """序列化器元数据."""
        model = Ticket
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def create(self, validated_data):
        """创建工单时自动创建审批步骤."""
        from apps.users.models import User

        ticket = super().create(validated_data)

        approvers = []
        if ticket.template.approvers:
            approver_usernames = ticket.template.approvers.split(',')
            for username in approver_usernames[:ticket.template.approval_steps]:
                try:
                    user = User.objects.get(username=username.strip())
                    approvers.append(user)
                except User.DoesNotExist:
                    pass

        if not approvers and ticket.template.created_by:
            approvers = [ticket.template.created_by]

        for i, approver in enumerate(approvers):
            ApprovalStep.objects.create(
                ticket=ticket,
                step=i,
                approver=approver
            )
        return ticket


class TicketListSerializer(serializers.ModelSerializer):
    """工单列表序列化器（简化版本）.

    用于列表展示，不包含完整的审批步骤详情。

    示例:
        >>> serializer = TicketListSerializer(tickets, many=True)
        >>> serializer.data
        [{'id': 1, 'title': '申请服务器', 'template_name': '服务器申请', ...}, ...]
    """

    template_name = serializers.CharField(
        source='template.name',
        read_only=True,
        help_text='模板名称'
    )
    applicant_name = serializers.CharField(
        source='applicant.username',
        read_only=True,
        help_text='申请人用户名'
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
        help_text='状态描述'
    )

    class Meta:
        """序列化器元数据."""
        model = Ticket
        fields = [
            'id', 'title', 'template', 'template_name',
            'applicant', 'applicant_name', 'status', 'status_display',
            'current_step', 'created_at'
        ]
