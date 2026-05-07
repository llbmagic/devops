from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessLineViewSet, TagViewSet, HostViewSet

router = DefaultRouter()
router.register(r'business-lines', BusinessLineViewSet)
router.register(r'tags', TagViewSet)
router.register(r'hosts', HostViewSet)

urlpatterns = [path('', include(router.urls))]