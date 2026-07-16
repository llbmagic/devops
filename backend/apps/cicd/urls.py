from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JenkinsInstanceViewSet, JenkinsJobViewSet,
    BuildRecordViewSet, PipelineViewSet,
    ReleaseOrderViewSet, JenkinsWebhookViewSet
)

router = DefaultRouter()
router.register(r'jenkins-instances', JenkinsInstanceViewSet)
router.register(r'jobs', JenkinsJobViewSet)
router.register(r'builds', BuildRecordViewSet)
router.register(r'pipelines', PipelineViewSet)
router.register(r'release-orders', ReleaseOrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('webhooks/jenkins/', JenkinsWebhookViewSet.as_view({'post': 'create'})),
]
