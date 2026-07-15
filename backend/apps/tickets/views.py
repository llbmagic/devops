"""工单审批模块视图集.

提供工单审批相关的 ViewSet。

API 路由:
    - /api/tickets/templates/ - 工单模板 CRUD
    - /api/tickets/ - 工单列表
    - /api/tickets/{id}/ - 工单详情
    - /api/tickets/{id}/submit/ - 提交工单
    - /api/tickets/{id}/approve/ - 审批工单
    - /api/tickets/{id}/reject/ - 拒绝工单
    - /api/tickets/{id}/close/ - 关闭工单
    - /api/tickets/my_tickets/ - 我的待审批
"""

import logging
from typing import Optional

from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from .models import TicketTemplate, Ticket, ApprovalStep, ApprovalRecord
from .serializers import (
    TicketTemplateSerializer, TicketSerializer, TicketListSerializer
)

logger = logging.getLogger(__name__)


class TicketTemplateViewSet(viewsets.ModelViewSet):
    """工单模板视图集.

    提供工单模板的完整 CRUD 操作。

    路由:
        GET /api/tickets/templates/ - 获取模板列表
        POST /api/tickets/templates/ - 创建模板
        GET /api/tickets/templates/{id}/ - 获取模板详情
        PUT /api/tickets/templates/{id}/ - 更新模板
        DELETE /api/tickets/templates/{id}/ - 删除模板

    示例:
        >>> requests.post('/api/tickets/templates/', json={
        ...     'name': '服务器申请',
        ...     'code': 'server_request',
        ...     'approvers': 'admin,manager'
        ... })
    """

    queryset = TicketTemplate.objects.all()
    serializer_class = TicketTemplateSerializer


class TicketViewSet(viewsets.ModelViewSet):
    """工单视图集.

    提供工单的完整 CRUD 操作，支持工单提交、审批、拒绝、关闭等操作。

    路由:
        GET /api/tickets/ - 获取工单列表
        POST /api/tickets/ - 创建工单
        GET /api/tickets/{id}/ - 获取工单详情
        PUT /api/tickets/{id}/ - 更新工单
        DELETE /api/tickets/{id}/ - 删除工单
        POST /api/tickets/{id}/submit/ - 提交工单
        POST /api/tickets/{id}/approve/ - 批准工单
        POST /api/tickets/{id}/reject/ - 拒绝工单
        POST /api/tickets/{id}/close/ - 关闭工单
        GET /api/tickets/my_tickets/ - 获取待我审批的工单

    筛选参数:
        - template: 按模板 ID 筛选
        - status: 按状态筛选
        - applicant: 按申请人 ID 筛选

    示例:
        >>> requests.get('/api/tickets/')
        >>> requests.get('/api/tickets/?status=pending')
        >>> requests.post('/api/tickets/1/submit/')
        >>> requests.post('/api/tickets/1/approve/', json={'comment': '同意'})
    """

    queryset = Ticket.objects.select_related(
        'template', 'applicant'
    ).prefetch_related(
        'approval_steps', 'approval_steps__approver'
    ).all()
    serializer_class = TicketSerializer

    def get_serializer_class(self):
        """列表使用简化版本，详情使用完整版本."""
        if self.action == 'list':
            return TicketListSerializer
        return TicketSerializer

    def get_queryset(self):
        """支持多条件筛选."""
        queryset = super().get_queryset()
        template_id = self.request.query_params.get('template')
        status = self.request.query_params.get('status')
        applicant_id = self.request.query_params.get('applicant')

        if template_id:
            queryset = queryset.filter(template_id=template_id)
        if status:
            queryset = queryset.filter(status=status)
        if applicant_id:
            queryset = queryset.filter(applicant_id=applicant_id)

        if self.action == 'my_tickets':
            queryset = queryset.filter(
                Q(status='pending') &
                Q(approval_steps__approver=self.request.user) &
                Q(approval_steps__status='pending')
            ).distinct()

        return queryset

    @action(detail=True, methods=['post'])
    def submit(self, request: Request, pk: Optional[str] = None) -> Response:
        """提交工单.

        将工单从草稿状态提交到待审批状态。只有申请人可以提交自己的工单。

        Returns:
            包含提交结果的响应。

        示例:
            POST /api/tickets/1/submit/
            Response: {'status': 'submitted'}
        """
        ticket = self.get_object()

        if ticket.applicant != request.user:
            return Response({'error': '只有申请人可以提交工单'}, status=403)

        if ticket.status != 'draft':
            return Response({'error': '只有草稿状态的工单可以提交'}, status=400)

        ticket.status = 'pending'
        ticket.save()

        logger.info(f"用户 {request.user.username} 提交了工单 {ticket.title}")
        return Response({'status': 'submitted'})

    @action(detail=True, methods=['post'])
    def approve(self, request: Request, pk: Optional[str] = None) -> Response:
        """批准工单.

        当前步骤的审批人批准工单，进入下一步或完成审批。

        Args:
            request: 包含 comment（审批意见）参数。

        Returns:
            包含批准结果的响应。

        示例:
            POST /api/tickets/1/approve/
            Body: {'comment': '同意申请'}
            Response: {'status': 'approved', 'ticket_status': 'approved'}
        """
        ticket = self.get_object()
        comment = request.data.get('comment', '')

        if ticket.status not in ['pending']:
            return Response({'error': '工单不在待审批状态'}, status=400)

        current_step_obj = ticket.approval_steps.filter(
            step=ticket.current_step
        ).first()

        if not current_step_obj:
            return Response({'error': '未找到当前审批步骤'}, status=400)

        if current_step_obj.approver != request.user:
            return Response({'error': '您不是当前步骤的审批人'}, status=403)

        if current_step_obj.status != 'pending':
            return Response({'error': '该步骤已完成审批'}, status=400)

        current_step_obj.status = 'approved'
        current_step_obj.comment = comment
        current_step_obj.completed_at = timezone.now()
        current_step_obj.save()

        ApprovalRecord.objects.create(
            step=current_step_obj,
            operator=request.user,
            action='approve',
            comment=comment
        )

        total_steps = ticket.approval_steps.count()
        if ticket.current_step >= total_steps - 1:
            ticket.status = 'approved'
            ticket.closed_at = timezone.now()
        else:
            ticket.current_step += 1

        ticket.save()

        logger.info(f"用户 {request.user.username} 批准了工单 {ticket.title}")
        return Response({'status': 'approved', 'ticket_status': ticket.status})

    @action(detail=True, methods=['post'])
    def reject(self, request: Request, pk: Optional[str] = None) -> Response:
        """拒绝工单.

        审批人拒绝工单，工单状态变为已拒绝。

        Args:
            request: 包含 comment（审批意见）参数。

        Returns:
            包含拒绝结果的响应。

        示例:
            POST /api/tickets/1/reject/
            Body: {'comment': '资源不足，暂不批准'}
            Response: {'status': 'rejected'}
        """
        ticket = self.get_object()
        comment = request.data.get('comment', '')

        if ticket.status != 'pending':
            return Response({'error': '工单不在待审批状态'}, status=400)

        current_step_obj = ticket.approval_steps.filter(
            step=ticket.current_step
        ).first()

        if not current_step_obj:
            return Response({'error': '未找到当前审批步骤'}, status=400)

        if current_step_obj.approver != request.user:
            return Response({'error': '您不是当前步骤的审批人'}, status=403)

        current_step_obj.status = 'rejected'
        current_step_obj.comment = comment
        current_step_obj.completed_at = timezone.now()
        current_step_obj.save()

        ApprovalRecord.objects.create(
            step=current_step_obj,
            operator=request.user,
            action='reject',
            comment=comment
        )

        ticket.status = 'rejected'
        ticket.closed_at = timezone.now()
        ticket.save()

        logger.info(f"用户 {request.user.username} 拒绝了工单 {ticket.title}")
        return Response({'status': 'rejected'})

    @action(detail=True, methods=['post'])
    def close(self, request: Request, pk: Optional[str] = None) -> Response:
        """关闭工单.

        申请人可以关闭自己的工单（只能是草稿或已批准状态）。

        Returns:
            包含关闭结果的响应。

        示例:
            POST /api/tickets/1/close/
            Response: {'status': 'closed'}
        """
        ticket = self.get_object()

        if ticket.applicant != request.user:
            return Response({'error': '只有申请人可以关闭工单'}, status=403)

        if ticket.status not in ['draft', 'approved']:
            return Response({'error': '该状态下的工单不能关闭'}, status=400)

        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.save()

        logger.info(f"用户 {request.user.username} 关闭了工单 {ticket.title}")
        return Response({'status': 'closed'})

    @action(detail=False, methods=['get'])
    def my_tickets(self, request: Request) -> Response:
        """获取待我审批的工单.

        Returns:
            待审批工单列表。

        示例:
            GET /api/tickets/my_tickets/
        """
        tickets = self.get_queryset()
        serializer = TicketListSerializer(tickets, many=True)
        return Response(serializer.data)
