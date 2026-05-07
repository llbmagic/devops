from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PrometheusInstanceViewSet, AlertRuleViewSet,
    AlertRecordViewSet, MonitorTargetViewSet, AlertmanagerWebhookViewset
)

router = DefaultRouter()
router.register(r'prometheus-instances', PrometheusInstanceViewSet)
router.register(r'alert-rules', AlertRuleViewSet)
router.register(r'alerts', AlertRecordViewSet)
router.register(r'targets', MonitorTargetViewSet)
router.register(r'webhooks', AlertmanagerWebhookViewset, basename='webhooks')

urlpatterns = [path('', include(router.urls))]