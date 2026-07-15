from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BusinessLineViewSet, EnvironmentViewSet, ApplicationViewSet,
    ClusterViewSet, TagViewSet, HostViewSet, ApplicationDependencyViewSet
)

router = DefaultRouter()
router.register(r'business-lines', BusinessLineViewSet)
router.register(r'environments', EnvironmentViewSet)
router.register(r'applications', ApplicationViewSet)
router.register(r'clusters', ClusterViewSet)
router.register(r'tags', TagViewSet)
router.register(r'hosts', HostViewSet)
router.register(r'application-dependencies', ApplicationDependencyViewSet)

urlpatterns = [path('', include(router.urls))]