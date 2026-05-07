from rest_framework import serializers
from .models import PrometheusInstance, AlertRule, AlertRecord, MonitorTarget


class PrometheusInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrometheusInstance
        fields = '__all__'
        extra_kwargs = {'api_token': {'write_only': True}}


class AlertRuleSerializer(serializers.ModelSerializer):
    prometheus_name = serializers.CharField(source='prometheus.name', read_only=True)

    class Meta:
        model = AlertRule
        fields = '__all__'


class AlertRecordSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source='rule.name', read_only=True)

    class Meta:
        model = AlertRecord
        fields = '__all__'


class MonitorTargetSerializer(serializers.ModelSerializer):
    prometheus_name = serializers.CharField(source='prometheus.name', read_only=True)
    host_ip = serializers.CharField(source='host.ip_address', read_only=True)

    class Meta:
        model = MonitorTarget
        fields = '__all__'