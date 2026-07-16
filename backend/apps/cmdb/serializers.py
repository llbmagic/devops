"""CMDB 模块序列化器.

提供资产管理相关的序列化器和反序列化器。
"""

from rest_framework import serializers
from .models import (
    AssetTypeDefinition, LocationNode, BusinessServiceNode,
    Tag, CloudAccount, Asset, AssetTag, Relationship, AssetChangeLog
)


class AssetTypeDefinitionSerializer(serializers.ModelSerializer):
    """资产类型定义序列化器."""

    class Meta:
        model = AssetTypeDefinition
        fields = '__all__'


class LocationNodeSerializer(serializers.ModelSerializer):
    """位置节点序列化器."""

    children = serializers.SerializerMethodField(
        help_text='子节点列表'
    )
    value = serializers.CharField(source='id', read_only=True)
    label = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = LocationNode
        fields = ['id', 'parent', 'name', 'type', 'code', 'description',
                  'created_at', 'children', 'value', 'label']
        read_only_fields = ['id', 'created_at']

    def get_children(self, obj):
        children = obj.children.all()
        return LocationNodeSerializer(children, many=True).data if children else []


class LocationNodeSimpleSerializer(serializers.ModelSerializer):
    """位置节点简单序列化器（用于下拉选择）."""

    class Meta:
        model = LocationNode
        fields = ['id', 'name', 'code', 'type']


class BusinessServiceNodeSerializer(serializers.ModelSerializer):
    """服务树节点序列化器."""

    children = serializers.SerializerMethodField(
        help_text='子节点列表'
    )
    value = serializers.CharField(source='id', read_only=True)
    label = serializers.CharField(source='name', read_only=True)

    class Meta:
        model = BusinessServiceNode
        fields = ['id', 'parent', 'name', 'type', 'code', 'description',
                  'created_at', 'children', 'value', 'label']
        read_only_fields = ['id', 'created_at']

    def get_children(self, obj):
        children = obj.children.all()
        return BusinessServiceNodeSerializer(children, many=True).data if children else []


class BusinessServiceNodeSimpleSerializer(serializers.ModelSerializer):
    """服务树节点简单序列化器（用于下拉选择）."""

    class Meta:
        model = BusinessServiceNode
        fields = ['id', 'name', 'code', 'type']


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器."""

    asset_count = serializers.SerializerMethodField(
        help_text='使用次数'
    )

    class Meta:
        model = Tag
        fields = ['id', 'key', 'value', 'asset_count', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_asset_count(self, obj):
        return obj.asset_tags.count()


class CloudAccountSerializer(serializers.ModelSerializer):
    """云账号序列化器."""

    provider_display = serializers.CharField(
        source='get_provider_display',
        read_only=True
    )

    class Meta:
        model = CloudAccount
        fields = [
            'id', 'provider', 'provider_display', 'name', 'account_id',
            'access_key', 'secret_key', 'region', 'description',
            'is_active', 'last_sync_at', 'created_at'
        ]
        read_only_fields = ['id', 'last_sync_at', 'created_at']
        extra_kwargs = {
            'secret_key': {'write_only': True}
        }


class AssetTagSerializer(serializers.ModelSerializer):
    """资产标签关联序列化器."""

    tag_key = serializers.CharField(source='tag.key', read_only=True)
    tag_value = serializers.CharField(source='tag.value', read_only=True)

    class Meta:
        model = AssetTag
        fields = ['id', 'asset', 'tag', 'tag_key', 'tag_value', 'created_at']
        read_only_fields = ['id', 'created_at']


class AssetChangeLogSerializer(serializers.ModelSerializer):
    """资产变更日志序列化器."""

    asset_name = serializers.CharField(source='asset.name', read_only=True)

    class Meta:
        model = AssetChangeLog
        fields = ['id', 'asset', 'asset_name', 'field', 'old_value',
                  'new_value', 'operator', 'source', 'created_at']
        read_only_fields = ['id', 'created_at']


class RelationshipSerializer(serializers.ModelSerializer):
    """资产关系序列化器."""

    source_name = serializers.CharField(source='source.name', read_only=True)
    target_name = serializers.CharField(source='target.name', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = Relationship
        fields = ['id', 'source', 'source_name', 'target', 'target_name',
                  'type', 'type_display', 'description', 'created_at']
        read_only_fields = ['id', 'created_at']


class AssetListSerializer(serializers.ModelSerializer):
    """资产列表序列化器（简化版本）."""

    asset_type_display = serializers.CharField(
        source='get_asset_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    location_name = serializers.CharField(
        source='location.name',
        read_only=True,
        allow_null=True
    )
    business_node_name = serializers.CharField(
        source='business_node.name',
        read_only=True,
        allow_null=True
    )
    tags = serializers.SerializerMethodField(
        help_text='标签列表'
    )

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'asset_type', 'asset_type_display',
            'unique_id', 'status', 'status_display',
            'location', 'location_name',
            'business_node', 'business_node_name',
            'owner', 'tags', 'created_at', 'updated_at'
        ]

    def get_tags(self, obj):
        return [f"{at.tag.key}:{at.tag.value}" for at in obj.asset_tags.all()]


class AssetDetailSerializer(serializers.ModelSerializer):
    """资产详情序列化器（完整版本）."""

    asset_type_display = serializers.CharField(
        source='get_asset_type_display',
        read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    location_info = LocationNodeSimpleSerializer(
        source='location',
        read_only=True,
        allow_null=True
    )
    business_node_info = BusinessServiceNodeSimpleSerializer(
        source='business_node',
        read_only=True,
        allow_null=True
    )
    tags = serializers.SerializerMethodField(
        help_text='标签详情列表'
    )
    change_logs = AssetChangeLogSerializer(
        source='change_logs',
        many=True,
        read_only=True,
        help_text='变更历史'
    )

    class Meta:
        model = Asset
        fields = [
            'id', 'name', 'asset_type', 'asset_type_display',
            'unique_id', 'status', 'status_display',
            'location', 'location_info',
            'business_node', 'business_node_info',
            'properties', 'cloud_info',
            'owner', 'maintenance_expire',
            'tags', 'change_logs',
            'created_at', 'updated_at', 'discovered_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'discovered_at']

    def get_tags(self, obj):
        return [
            {'id': at.tag.id, 'key': at.tag.key, 'value': at.tag.value}
            for at in obj.asset_tags.all()
        ]


class AssetCreateSerializer(serializers.ModelSerializer):
    """创建资产序列化器."""

    tag_list = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        required=False,
        help_text='标签列表，格式：["key:value", "key2:value2"]'
    )

    class Meta:
        model = Asset
        fields = [
            'name', 'asset_type', 'unique_id', 'status',
            'location', 'business_node',
            'properties', 'cloud_info',
            'owner', 'maintenance_expire', 'tag_list'
        ]

    def create(self, validated_data):
        tag_list = validated_data.pop('tag_list', [])
        asset = Asset.objects.create(**validated_data)

        for tag_str in tag_list:
            if ':' in tag_str:
                key, value = tag_str.split(':', 1)
                tag, _ = Tag.objects.get_or_create(key=key, value=value)
                AssetTag.objects.get_or_create(asset=asset, tag=tag)

        return asset