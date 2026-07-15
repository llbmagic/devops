"""Ansible 模块 URL 路由配置."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnsibleServerViewSet, PlaybookViewSet, TaskRecordViewSet

router = DefaultRouter()
router.register(r'servers', AnsibleServerViewSet)
router.register(r'playbooks', PlaybookViewSet)
router.register(r'records', TaskRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
