import requests
from django.conf import settings
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import PrometheusInstance, AlertRule, AlertRecord, MonitorTarget
from .serializers import (
    PrometheusInstanceSerializer, AlertRuleSerializer,
    AlertRecordSerializer, MonitorTargetSerializer
)


class PrometheusInstanceViewSet(viewsets.ModelViewSet):
    queryset = PrometheusInstance.objects.all()
    serializer_class = PrometheusInstanceSerializer

    @action(detail=True, methods=['get'])
    def query(self, request, pk=None):
        """查询 Prometheus 指标"""
        instance = self.get_object()
        query = request.query_params.get('query', '')
        url = f"{instance.url}/api/v1/query"
        headers = {'Authorization': f"Bearer {instance.api_token}"} if instance.api_token else {}
        response = requests.get(url, params={'query': query}, headers=headers, timeout=10)
        return Response(response.json())

    @action(detail=True, methods=['get'])
    def targets(self, request, pk=None):
        """获取监控目标列表"""
        instance = self.get_object()
        url = f"{instance.url}/api/v1/targets"
        headers = {'Authorization': f"Bearer {instance.api_token}"} if instance.api_token else {}
        response = requests.get(url, headers=headers, timeout=10)
        return Response(response.json())


class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.select_related('prometheus').all()
    serializer_class = AlertRuleSerializer

    @action(detail=False, methods=['get'])
    def by_severity(self, request):
        severity = request.query_params.get('severity')
        queryset = self.get_queryset()
        if severity:
            queryset = queryset.filter(severity=severity)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AlertRecordViewSet(viewsets.ModelViewSet):
    queryset = AlertRecord.objects.select_related('rule').all()
    serializer_class = AlertRecordSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.query_params.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=True, methods=['patch'])
    def acknowledge(self, request, pk=None):
        record = self.get_object()
        record.status = 'acknowledged'
        record.acknowledged_by = request.user.username
        record.save()
        return Response({'status': 'acknowledged'})


class MonitorTargetViewSet(viewsets.ModelViewSet):
    queryset = MonitorTarget.objects.select_related('prometheus', 'host').all()
    serializer_class = MonitorTargetSerializer


class AlertmanagerWebhookViewset(viewsets.ViewSet):
    """Alertmanager Webhook 接收"""
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def alertmanager(self, request):
        """接收 Alertmanager 告警"""
        alerts = request.data.get('alerts', [])
        for alert in alerts:
            labels = alert.get('labels', {})
            annotations = alert.get('annotations', {})
            status = 'firing' if alert.get('status') == 'firing' else 'resolved'

            # 查找或创建告警规则
            alert_name = labels.get('alertname', 'unknown')
            rule, _ = AlertRule.objects.get_or_create(
                name=alert_name,
                defaults={'expr': 'unknown', 'prometheus_id': 1}
            )

            AlertRecord.objects.create(
                rule=rule,
                status=status,
                alert_name=alert_name,
                labels=labels,
                annotations=annotations,
                starts_at=alert.get('startsAt')
            )
        return Response({'status': 'received'})