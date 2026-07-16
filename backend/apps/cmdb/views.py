"""CMDB 模块视图集.

提供资产管理的完整 CRUD 操作，包括生命周期管理、关系管理、
位置树、服务树、云账号配置和自动纳管接口。
"""

import logging
import json
from typing import Optional
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from .models import (
    AssetTypeDefinition, LocationNode, BusinessServiceNode,
    Tag, CloudAccount, Asset, AssetTag, Relationship, AssetChangeLog
)
from .serializers import (
    AssetTypeDefinitionSerializer,
    LocationNodeSerializer, LocationNodeSimpleSerializer,
    BusinessServiceNodeSerializer, BusinessServiceNodeSimpleSerializer,
    TagSerializer, CloudAccountSerializer,
    AssetListSerializer, AssetDetailSerializer, AssetCreateSerializer,
    AssetTagSerializer,
    RelationshipSerializer,
    AssetChangeLogSerializer
)

logger = logging.getLogger(__name__)


class AssetViewSet(viewsets.ModelViewSet):
    """资产视图集."""

    queryset = Asset.objects.select_related(
        'location', 'business_node'
    ).prefetch_related('asset_tags__tag', 'change_logs').filter(
        is_deleted=False
    ).all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AssetListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return AssetCreateSerializer
        return AssetDetailSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        asset_type = self.request.query_params.get('asset_type')
        status = self.request.query_params.get('status')
        location_id = self.request.query_params.get('location')
        business_node_id = self.request.query_params.get('business_node')
        keyword = self.request.query_params.get('keyword')

        if asset_type:
            queryset = queryset.filter(asset_type=asset_type)
        if status:
            queryset = queryset.filter(status=status)
        if location_id:
            queryset = queryset.filter(location_id=location_id)
        if business_node_id:
            queryset = queryset.filter(business_node_id=business_node_id)
        if keyword:
            queryset = queryset.filter(
                Q(name__icontains=keyword) |
                Q(unique_id__icontains=keyword) |
                Q(owner__icontains=keyword)
            )

        return queryset

    def perform_update(self, serializer):
        old_instance = self.get_object()
        old_values = {
            field: getattr(old_instance, field)
            for field in ['name', 'status', 'owner', 'location_id',
                         'business_node_id', 'properties']
        }

        instance = serializer.save()

        new_values = {
            'name': instance.name,
            'status': instance.status,
            'owner': instance.owner,
            'location_id': instance.location_id,
            'business_node_id': instance.business_node_id,
            'properties': instance.properties
        }

        for field, old_val in old_values.items():
            new_val = new_values.get(field)
            if old_val != new_val:
                AssetChangeLog.objects.create(
                    asset=instance,
                    field=field,
                    old_value=str(old_val) if old_val is not None else '',
                    new_value=str(new_val) if new_val is not None else '',
                    operator=self.request.user.username if self.request.user.is_authenticated else 'system',
                    source='manual'
                )

        logger.info(f"用户 {self.request.user.username} 更新了资产 {instance.name}")

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()
        logger.info(f"用户 {self.request.user.username} 删除了资产 {instance.name}")

    @action(detail=True, methods=['post'])
    def lifecycle(self, request: Request, pk: Optional[str] = None) -> Response:
        """生命周期操作."""
        asset = self.get_object()
        action_type = request.data.get('action')

        valid_actions = ['approve', 'reject', 'online', 'offline',
                        'maintenance', 'decommission', 'archive']
        if action_type not in valid_actions:
            return Response({'error': f'无效操作，可选：{valid_actions}'}, status=400)

        old_status = asset.status
        status_mapping = {
            'approve': 'online',
            'reject': 'archived',
            'online': 'online',
            'offline': 'offline',
            'maintenance': 'maintenance',
            'decommission': 'decommissioned',
            'archive': 'archived'
        }

        asset.status = status_mapping[action_type]
        asset.save()

        AssetChangeLog.objects.create(
            asset=asset,
            field='status',
            old_value=old_status,
            new_value=asset.status,
            operator=request.user.username if request.user.is_authenticated else 'system',
            source='manual'
        )

        logger.info(f"资产 {asset.name} 状态变更：{old_status} -> {asset.status}")
        return Response({'status': asset.status})

    @action(detail=True, methods=['get'])
    def relationships(self, request: Request, pk: Optional[str] = None) -> Response:
        """获取资产关联关系."""
        asset = self.get_object()
        rel_type = request.query_params.get('type')

        outgoing = asset.outgoing_relationships.all()
        incoming = asset.incoming_relationships.all()

        if rel_type:
            outgoing = outgoing.filter(type=rel_type)
            incoming = incoming.filter(type=rel_type)

        return Response({
            'outgoing': RelationshipSerializer(outgoing, many=True).data,
            'incoming': RelationshipSerializer(incoming, many=True).data
        })

    @action(detail=True, methods=['get'])
    def history(self, request: Request, pk: Optional[str] = None) -> Response:
        """获取变更历史."""
        asset = self.get_object()
        logs = asset.change_logs.all()[:50]
        return Response(AssetChangeLogSerializer(logs, many=True).data)

    @action(detail=False, methods=['post'])
    def auto_discover(self, request: Request) -> Response:
        """Agent 批量上报接口."""
        agent_id = request.data.get('agent_id')
        discoveries = request.data.get('discoveries', [])

        if not discoveries:
            return Response({'error': 'discoveries 不能为空'}, status=400)

        created_count = 0
        updated_count = 0

        for item in discoveries:
            unique_id = item.get('unique_id')
            if not unique_id:
                continue

            properties = item.get('properties', {})
            defaults = {
                'name': item.get('name', unique_id),
                'asset_type': item.get('asset_type', 'server'),
                'status': 'online',
                'properties': properties,
                'owner': item.get('owner'),
            }

            asset, created = Asset.objects.update_or_create(
                unique_id=unique_id,
                defaults=defaults
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

            location_code = item.get('location_code')
            if location_code:
                try:
                    location = LocationNode.objects.get(code=location_code)
                    asset.location = location
                    asset.save()
                except LocationNode.DoesNotExist:
                    pass

            tags = item.get('tags', [])
            for tag_str in tags:
                if ':' in tag_str:
                    key, value = tag_str.split(':', 1)
                    tag, _ = Tag.objects.get_or_create(key=key, value=value)
                    AssetTag.objects.get_or_create(asset=asset, tag=tag)

            AssetChangeLog.objects.create(
                asset=asset,
                field='discovered',
                old_value='',
                new_value=f'Agent {agent_id} 发现',
                operator=agent_id,
                source='agent'
            )

        logger.info(f"Agent {agent_id} 上报完成：新建 {created_count}，更新 {updated_count}")
        return Response({
            'created': created_count,
            'updated': updated_count,
            'agent_id': agent_id
        })


class RelationshipViewSet(viewsets.ModelViewSet):
    """资产关系视图集."""

    queryset = Relationship.objects.select_related('source', 'target').all()
    serializer_class = RelationshipSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        rel_type = self.request.query_params.get('type')
        source_id = self.request.query_params.get('source')
        target_id = self.request.query_params.get('target')

        if rel_type:
            queryset = queryset.filter(type=rel_type)
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        if target_id:
            queryset = queryset.filter(target_id=target_id)

        return queryset


class LocationNodeViewSet(viewsets.ModelViewSet):
    """位置节点视图集."""

    queryset = LocationNode.objects.prefetch_related('children').all()
    serializer_class = LocationNodeSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return LocationNodeSerializer
        return LocationNodeSerializer


class BusinessServiceNodeViewSet(viewsets.ModelViewSet):
    """服务树节点视图集."""

    queryset = BusinessServiceNode.objects.prefetch_related('children').all()
    serializer_class = BusinessServiceNodeSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return BusinessServiceNodeSerializer
        return BusinessServiceNodeSerializer

    @action(detail=True, methods=['post'])
    def attach(self, request: Request, pk: Optional[str] = None) -> Response:
        """挂载资产到服务节点."""
        node = self.get_object()
        asset_ids = request.data.get('asset_ids', [])

        if not asset_ids:
            return Response({'error': 'asset_ids 不能为空'}, status=400)

        updated = Asset.objects.filter(id__in=asset_ids).update(business_node=node)
        logger.info(f"用户 {request.user.username} 将 {updated} 个资产挂载到服务节点 {node.name}")
        return Response({'attached': updated})


class TagViewSet(viewsets.ModelViewSet):
    """标签视图集."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class AssetTypeDefinitionViewSet(viewsets.ModelViewSet):
    """资产类型定义视图集."""

    queryset = AssetTypeDefinition.objects.filter(is_active=True).all()
    serializer_class = AssetTypeDefinitionSerializer


class CloudAccountViewSet(viewsets.ModelViewSet):
    """云账号视图集."""

    queryset = CloudAccount.objects.all()
    serializer_class = CloudAccountSerializer

    @action(detail=True, methods=['post'])
    def sync(self, request: Request, pk: Optional[str] = None) -> Response:
        """触发云账号同步."""
        account = self.get_object()
        # TODO: 实现实际的云平台同步逻辑
        # 这里只是模拟同步操作
        from django.utils import timezone
        account.last_sync_at = timezone.now()
        account.save()
        logger.info(f"用户 {request.user.username} 触发了云账号 {account.name} 的同步")
        return Response({'status': 'sync started', 'last_sync_at': account.last_sync_at})