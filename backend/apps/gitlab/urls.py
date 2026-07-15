"""GitLab 模块 URL 路由配置.

使用 DRF DefaultRouter 自动注册 ViewSet 路由。
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GitLabInstanceViewSet, ProjectViewSet, MergeRequestViewSet

router = DefaultRouter()
router.register(r'instances', GitLabInstanceViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'merge-requests', MergeRequestViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
