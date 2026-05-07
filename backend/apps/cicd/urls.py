from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import JenkinsInstanceViewSet, JenkinsJobViewSet, BuildRecordViewSet, PipelineViewSet

router = DefaultRouter()
router.register(r'jenkins-instances', JenkinsInstanceViewSet)
router.register(r'jobs', JenkinsJobViewSet)
router.register(r'builds', BuildRecordViewSet)
router.register(r'pipelines', PipelineViewSet)

urlpatterns = [path('', include(router.urls))]
