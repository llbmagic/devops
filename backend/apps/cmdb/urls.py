from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AssetViewSet, RelationshipViewSet,
    LocationNodeViewSet, BusinessServiceNodeViewSet,
    TagViewSet, AssetTypeDefinitionViewSet, CloudAccountViewSet
)

router = DefaultRouter()
router.register(r'assets', AssetViewSet)
router.register(r'relationships', RelationshipViewSet)
router.register(r'locations', LocationNodeViewSet)
router.register(r'business-tree', BusinessServiceNodeViewSet)
router.register(r'tags', TagViewSet)
router.register(r'asset-types', AssetTypeDefinitionViewSet)
router.register(r'cloud-accounts', CloudAccountViewSet)

urlpatterns = [
    path('', include(router.urls)),
]