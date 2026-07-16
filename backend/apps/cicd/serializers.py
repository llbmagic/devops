from rest_framework import serializers
from .models import JenkinsInstance, JenkinsJob, BuildRecord, Pipeline, ReleaseOrder, ReleaseRecord
from apps.tickets.models import ApprovalStep, ApprovalRecord


class JenkinsInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = JenkinsInstance
        fields = '__all__'
        extra_kwargs = {'api_token': {'write_only': True}}


class JenkinsJobSerializer(serializers.ModelSerializer):
    instance_name = serializers.CharField(source='instance.name', read_only=True)

    class Meta:
        model = JenkinsJob
        fields = '__all__'


class BuildRecordSerializer(serializers.ModelSerializer):
    job_name = serializers.CharField(source='job.name', read_only=True)

    class Meta:
        model = BuildRecord
        fields = '__all__'
        read_only_fields = ['id', 'started_at']


class PipelineSerializer(serializers.ModelSerializer):
    job_name = serializers.CharField(source='job.name', read_only=True)

    class Meta:
        model = Pipeline
        fields = '__all__'


class ReleaseRecordSerializer(serializers.ModelSerializer):
    """发布执行记录序列化器."""

    release_order_title = serializers.CharField(
        source='release_order.title',
        read_only=True,
        help_text='发布单标题'
    )
    build_record_id = serializers.IntegerField(
        source='build_record.id',
        read_only=True,
        help_text='构建记录ID'
    )

    class Meta:
        model = ReleaseRecord
        fields = '__all__'
        read_only_fields = ['id', 'started_at']


class ApprovalStepSerializer(serializers.ModelSerializer):
    """审批步骤序列化器（复用 tickets 模块）。

    用于序列化发布单的审批步骤。

    新增字段:
        approver_name: 审批人用户名（只读）。
        status_display: 状态描述（只读）。
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

    class Meta:
        model = ApprovalStep
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ApprovalRecordSerializer(serializers.ModelSerializer):
    """审批记录序列化器（复用 tickets 模块）。

    新增字段:
        operator_name: 操作人用户名（只读）。
        action_display: 操作描述（只读）。
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
        model = ApprovalRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class ReleaseOrderSerializer(serializers.ModelSerializer):
    """发布单序列化器."""

    jenkins_job_name = serializers.CharField(
        source='jenkins_job.name',
        read_only=True,
        help_text='Jenkins Job 名称'
    )
    jenkins_instance_name = serializers.CharField(
        source='jenkins_job.instance.name',
        read_only=True,
        help_text='Jenkins 实例名称'
    )
    applicant_name = serializers.CharField(
        source='applicant.username',
        read_only=True,
        help_text='申请人用户名'
    )
    status_display = serializers.SerializerMethodField(
        help_text='状态描述'
    )
    approval_steps = serializers.SerializerMethodField(
        help_text='审批步骤列表'
    )
    release_records = ReleaseRecordSerializer(
        source='release_records',
        many=True,
        read_only=True,
        help_text='发布执行记录列表'
    )

    class Meta:
        model = ReleaseOrder
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_status_display(self, obj):
        return dict(ReleaseOrder.STATUS_CHOICES).get(obj.status, obj.status)

    def get_approval_steps(self, obj):
        steps = ApprovalStep.objects.filter(
            ticket_id=obj.id,
            ticket__isnull=False
        ).order_by('step')
        return ApprovalStepSerializer(steps, many=True).data


class ReleaseOrderListSerializer(serializers.ModelSerializer):
    """发布单列表序列化器（简化版本）。"""

    jenkins_job_name = serializers.CharField(
        source='jenkins_job.name',
        read_only=True,
        help_text='Jenkins Job 名称'
    )
    applicant_name = serializers.CharField(
        source='applicant.username',
        read_only=True,
        help_text='申请人用户名'
    )
    status_display = serializers.SerializerMethodField(
        help_text='状态描述'
    )

    class Meta:
        model = ReleaseOrder
        fields = [
            'id', 'title', 'jenkins_job', 'jenkins_job_name',
            'applicant', 'applicant_name', 'status', 'status_display',
            'execute_mode', 'scheduled_time', 'current_step', 'created_at'
        ]

    def get_status_display(self, obj):
        return dict(ReleaseOrder.STATUS_CHOICES).get(obj.status, obj.status)
