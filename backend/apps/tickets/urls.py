"""工单审批模块 URL 路由配置."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TicketTemplateViewSet, TicketViewSet

router = DefaultRouter()
router.register(r'templates', TicketTemplateViewSet)
router.register(r'', TicketViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
