"""CMDB 资产管理模块.

提供运维平台的资产全生命周期管理，包括统一资产模型、位置树、服务树、
关系管理、变更审计和云厂商适配器框架。

数据模型层次结构:
    位置树 (LocationNode)
        └── 机房/机柜

    服务树 (BusinessServiceNode)
        └── 业务线 → 服务 → 模块 → 实例

    资产 (Asset)
        ├── 物理服务器 (server)
        ├── 虚拟机 (vm)
        ├── 云主机 (cloud_vm)
        ├── 网络设备 (network_device)
        └── 存储设备 (storage)

关系类型:
    - runs_on: 运行于
    - depends_on: 依赖
    - connects_to: 连接

典型使用场景:
    - 资产全生命周期管理（上线、下线、维保、退役）
    - 位置树和服务树组织架构
    - 资产关系建模和依赖分析
    - 变更审计追溯
    - 多云资产统一纳管
"""

import logging
from django.db import models
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class AssetTypeDefinition(models.Model):
    """资产类型定义.

    定义各类资产的属性schema，支持动态扩展资产类型。

    属性:
        asset_type: 类型代码，唯一标识。
        name: 类型名称。
        property_schema: 属性schema定义（JSON）。
        icon: 前端图标。
        is_active: 是否启用。

    示例:
        >>> AssetTypeDefinition.objects.create(
        ...     asset_type='server',
        ...     name='物理服务器',
        ...     property_schema={'cpu': 'string', 'memory': 'string'}
        ... )
    """

    ASSET_TYPE_CHOICES = [
        ('server', '物理服务器'),
        ('vm', '虚拟机'),
        ('cloud_vm', '云主机'),
        ('network_device', '网络设备'),
        ('storage', '存储设备'),
    ]

    asset_type = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='类型代码',
        help_text='资产类型唯一标识'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='类型名称',
        help_text='资产类型的显示名称'
    )
    property_schema = models.JSONField(
        default=dict,
        verbose_name='属性Schema',
        help_text='属性定义JSON Schema'
    )
    icon = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='图标',
        help_text='前端显示图标'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='禁用的类型不会出现在选项中'
    )

    class Meta:
        db_table = 'asset_type_definition'
        verbose_name = '资产类型定义'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"{self.name}({self.asset_type})"


class LocationNode(models.Model):
    """位置树节点.

    按物理或逻辑区域组织的层级关系，支持多级层次。
    例如：华南区 → 深圳机房 → A区机柜 → 12号机柜

    属性:
        parent: 父节点，可为空（根节点）。
        name: 节点名称。
        type: 节点类型（region/zone/datacenter/rack/device）。
        code: 编码，唯一标识。
        description: 描述。
        created_at: 创建时间。

    示例:
        >>> region = LocationNode.objects.create(
        ...     name='华南区',
        ...     type='region',
        ...     code='south-china'
        ... )
        >>> datacenter = LocationNode.objects.create(
        ...     name='深圳机房',
        ...     type='datacenter',
        ...     code='sz-dc01',
        ...     parent=region
        ... )
    """

    TYPE_CHOICES = [
        ('region', '区域'),
        ('zone', '可用区'),
        ('datacenter', '机房'),
        ('rack', '机柜'),
        ('device', '设备位'),
    ]

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父节点',
        help_text='父节点，为空表示根节点'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='节点名称',
        help_text='位置节点的显示名称'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='节点类型',
        help_text='region-区域，zone-可用区，datacenter-机房，rack-机柜，device-设备位'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='编码',
        help_text='唯一标识代码'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='位置节点的详细描述'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'location_node'
        verbose_name = '位置节点'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self) -> str:
        return f"{self.name}({self.code})"


class BusinessServiceNode(models.Model):
    """服务树节点.

    以业务为中心的层级拓扑，描述业务系统、应用服务、运行实例之间的层次关系。
    例如：电商平台 → 订单服务 → 订单模块 → order-01实例

    属性:
        parent: 父节点，可为空（根节点）。
        name: 节点名称。
        type: 节点类型（business/service/module/instance）。
        code: 编码，唯一标识。
        description: 描述。
        created_at: 创建时间。

    示例:
        >>> business = BusinessServiceNode.objects.create(
        ...     name='电商平台',
        ...     type='business',
        ...     code='ecommerce'
        ... )
        >>> service = BusinessServiceNode.objects.create(
        ...     name='订单服务',
        ...     type='service',
        ...     code='order-service',
        ...     parent=business
        ... )
    """

    TYPE_CHOICES = [
        ('business', '业务线'),
        ('service', '服务'),
        ('module', '模块'),
        ('instance', '实例'),
    ]

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父节点',
        help_text='父节点，为空表示根节点'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='节点名称',
        help_text='服务节点的显示名称'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='节点类型',
        help_text='business-业务线，service-服务，module-模块，instance-实例'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='编码',
        help_text='唯一标识代码'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='服务节点的详细描述'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'business_service_node'
        verbose_name = '服务树节点'
        verbose_name_plural = verbose_name
        ordering = ['code']

    def __str__(self) -> str:
        return f"{self.name}({self.code})"


class Tag(models.Model):
    """标签定义.

    标签是资产的灵活分类标记，支持 key-value 形式。
    用于资产的分组、筛选和策略驱动。

    属性:
        key: 标签键。
        value: 标签值。
        created_at: 创建时间。

    示例:
        >>> Tag.objects.create(key='env', value='prod')
        >>> Tag.objects.create(key='team', value='sre')
    """

    key = models.CharField(
        max_length=50,
        verbose_name='标签键',
        help_text='标签的键，如 env、team、app'
    )
    value = models.CharField(
        max_length=100,
        verbose_name='标签值',
        help_text='标签的值'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'tag'
        verbose_name = '标签'
        verbose_name_plural = verbose_name
        unique_together = ['key', 'value']

    def __str__(self) -> str:
        return f"{self.key}:{self.value}"


class CloudAccount(models.Model):
    """云账号.

    管理多云平台的账号配置，用于云资源同步和统一纳管。
    支持阿里云、AWS、腾讯云、华为云、Azure、Google Cloud等主流云厂商。

    属性:
        provider: 云厂商。
        name: 账号名称。
        account_id: 云平台账号ID。
        access_key: 访问密钥。
        secret_key: 访问密钥密文。
        region: 默认区域。
        description: 描述。
        is_active: 是否启用。
        last_sync_at: 最后同步时间。
        created_at: 创建时间。

    示例:
        >>> CloudAccount.objects.create(
        ...     provider='aliyun',
        ...     name='阿里云主账号',
        ...     account_id='123456789',
        ...     access_key='access_key',
        ...     secret_key='secret_key',
        ...     region='cn-hangzhou'
        ... )
    """

    PROVIDER_CHOICES = [
        ('aliyun', '阿里云'),
        ('aws', 'AWS'),
        ('tencent', '腾讯云'),
        ('huawei', '华为云'),
        ('azure', 'Azure'),
        ('gcp', 'Google Cloud'),
    ]

    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        verbose_name='云厂商',
        help_text='云平台提供商'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='账号名称',
        help_text='云账号的显示名称'
    )
    account_id = models.CharField(
        max_length=100,
        verbose_name='账号ID',
        help_text='云平台的账号ID'
    )
    access_key = models.CharField(
        max_length=200,
        verbose_name='AccessKey',
        help_text='云平台的访问密钥ID'
    )
    secret_key = models.CharField(
        max_length=200,
        verbose_name='SecretKey',
        help_text='云平台的访问密钥密文'
    )
    region = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name='区域',
        help_text='云资源的默认区域'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='描述',
        help_text='云账号的详细描述'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用',
        help_text='禁用的账号不会进行同步'
    )
    last_sync_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='最后同步时间',
        help_text='最近一次同步的时间'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'cloud_account'
        verbose_name = '云账号'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.name}({self.get_provider_display()})"


class Asset(models.Model):
    """统一资产模型.

    统一的资产配置项，支持多种资产类型（物理服务器、虚拟机、云主机、网络设备、存储设备）。
    记录资产的全生命周期信息、配置参数、关联关系和变更历史。

    属性:
        name: 资产名称。
        asset_type: 资产类型。
        unique_id: 唯一标识（序列号/InstanceId）。
        status: 生命周期状态。
        location: 所属位置节点。
        business_node: 所属服务树节点。
        properties: 类型特有属性（JSON）。
        cloud_info: 云厂商原始信息（JSON）。
        owner: 负责人。
        maintenance_expire: 维保过期日期。
        created_at: 创建时间。
        updated_at: 更新时间。
        discovered_at: 发现时间。
        is_deleted: 软删除标记。

    状态流转:
        pending → online → maintenance → decommissioned → archived
            ↓         ↓          ↓
        rejected   offline    offline

    示例:
        >>> Asset.objects.create(
        ...     name='web-server-01',
        ...     asset_type='server',
        ...     unique_id='SN-12345',
        ...     status='online',
        ...     properties={'cpu': '8核', 'memory': '32GB'}
        ... )
    """

    ASSET_TYPE_CHOICES = [
        ('server', '物理服务器'),
        ('vm', '虚拟机'),
        ('cloud_vm', '云主机'),
        ('network_device', '网络设备'),
        ('storage', '存储设备'),
    ]

    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('online', '在线'),
        ('offline', '离线'),
        ('maintenance', '维护中'),
        ('decommissioned', '已下线'),
        ('archived', '已归档'),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name='资产名称',
        help_text='资产的显示名称'
    )
    asset_type = models.CharField(
        max_length=20,
        choices=ASSET_TYPE_CHOICES,
        verbose_name='资产类型',
        help_text='server-物理服务器，vm-虚拟机，cloud_vm-云主机，network_device-网络设备，storage-存储设备'
    )
    unique_id = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='唯一标识',
        help_text='资产的唯一标识，如序列号、云资源ID'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='状态',
        help_text='资产的生命周期状态'
    )
    location = models.ForeignKey(
        LocationNode,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assets',
        verbose_name='位置节点',
        help_text='资产所属的位置节点'
    )
    business_node = models.ForeignKey(
        BusinessServiceNode,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assets',
        verbose_name='服务树节点',
        help_text='资产所属的服务树节点'
    )
    properties = models.JSONField(
        default=dict,
        verbose_name='配置属性',
        help_text='资产类型特有的配置属性'
    )
    cloud_info = models.JSONField(
        null=True,
        blank=True,
        verbose_name='云厂商信息',
        help_text='云资源的原始元数据'
    )
    owner = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='负责人',
        help_text='资产负责人'
    )
    maintenance_expire = models.DateField(
        null=True,
        blank=True,
        verbose_name='维保过期日期',
        help_text='维保到期日期'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    discovered_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='发现时间',
        help_text='自动发现时的时间'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='软删除',
        help_text='标记为已删除，不物理删除'
    )

    class Meta:
        db_table = 'asset'
        verbose_name = '资产'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.name}({self.asset_type})"


class AssetTag(models.Model):
    """资产标签关联.

    资产与标签的多对多关联关系。

    属性:
        asset: 资产。
        tag: 标签。
        created_at: 创建时间。

    示例:
        >>> asset = Asset.objects.first()
        >>> tag = Tag.objects.get(key='env', value='prod')
        >>> AssetTag.objects.create(asset=asset, tag=tag)
    """

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='asset_tags',
        verbose_name='资产',
        help_text='关联的资产'
    )
    tag = models.ForeignKey(
        Tag,
        on_delete=models.CASCADE,
        related_name='asset_tags',
        verbose_name='标签',
        help_text='关联的标签'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'asset_tag'
        verbose_name = '资产标签'
        verbose_name_plural = verbose_name
        unique_together = ['asset', 'tag']

    def __str__(self) -> str:
        return f"{self.asset.name} - {self.tag}"


class Relationship(models.Model):
    """资产关系表.

    记录资产之间的关联关系，支持 runs_on、depends_on、connects_to 三种类型。

    属性:
        source: 源资产。
        target: 目标资产。
        type: 关系类型。
        description: 关系描述。
        created_at: 创建时间。

    示例:
        >>> vm = Asset.objects.get(unique_id='vm-001')
        >>> server = Asset.objects.get(unique_id='server-001')
        >>> Relationship.objects.create(
        ...     source=vm,
        ...     target=server,
        ...     type='runs_on',
        ...     description='虚拟机运行在物理服务器上'
        ... )
    """

    TYPE_CHOICES = [
        ('runs_on', '运行于'),
        ('depends_on', '依赖'),
        ('connects_to', '连接'),
    ]

    source = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='outgoing_relationships',
        verbose_name='源资产',
        help_text='关系的源资产'
    )
    target = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='incoming_relationships',
        verbose_name='目标资产',
        help_text='关系的目标资产'
    )
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        verbose_name='关系类型',
        help_text='runs_on-运行于，depends_on-依赖，connects_to-连接'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='关系描述',
        help_text='关系的详细说明'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        db_table = 'relationship'
        verbose_name = '资产关系'
        verbose_name_plural = verbose_name
        unique_together = ['source', 'target', 'type']

    def __str__(self) -> str:
        return f"{self.source.name} -{self.type}-> {self.target.name}"


class AssetChangeLog(models.Model):
    """资产变更日志.

    记录资产的每次属性变更，用于审计追溯。

    属性:
        asset: 资产。
        field: 变更字段。
        old_value: 旧值。
        new_value: 新值。
        operator: 操作人。
        source: 操作来源（manual/api/agent）。
        created_at: 操作时间。

    示例:
        >>> asset = Asset.objects.first()
        >>> AssetChangeLog.objects.create(
        ...     asset=asset,
        ...     field='status',
        ...     old_value='online',
        ...     new_value='maintenance',
        ...     operator='admin',
        ...     source='manual'
        ... )
    """

    SOURCE_CHOICES = [
        ('manual', '手动'),
        ('api', 'API'),
        ('agent', 'Agent'),
        ('sync', '云平台同步'),
    ]

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='change_logs',
        verbose_name='资产',
        help_text='变更的资产'
    )
    field = models.CharField(
        max_length=100,
        verbose_name='变更字段',
        help_text='被修改的字段名'
    )
    old_value = models.TextField(
        null=True,
        blank=True,
        verbose_name='旧值',
        help_text='修改前的值'
    )
    new_value = models.TextField(
        null=True,
        blank=True,
        verbose_name='新值',
        help_text='修改后的值'
    )
    operator = models.CharField(
        max_length=100,
        verbose_name='操作人',
        help_text='执行操作的用户'
    )
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default='manual',
        verbose_name='操作来源',
        help_text='manual-手动，api-API，agent-Agent，sync-云平台同步'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='操作时间'
    )

    class Meta:
        db_table = 'asset_change_log'
        verbose_name = '资产变更日志'
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.asset.name} - {self.field} @ {self.created_at}"


# ============ 兼容旧模型 ============
# 以下模型保留以保持与 cicd.Pipeline 和 monitor.MonitorTarget 的兼容性
# 新代码应使用 Asset 模型


class Host(models.Model):
    """主机模型（兼容旧版）.

    本模块已升级为统一 Asset 模型，此 Host 模型保留用于兼容现有引用。
    新代码请使用 Asset 模型。

    属性:
        hostname: 主机名。
        ip_address: IP 地址。
        status: 状态。
        business_line: 所属业务线。
        cluster: 所属集群。
    """

    STATUS_CHOICES = [
        ('online', '在线'),
        ('offline', '离线'),
        ('maintenance', '维护中'),
    ]

    hostname = models.CharField(max_length=100, verbose_name='主机名')
    ip_address = models.GenericIPAddressField(verbose_name='IP 地址')
    ssh_port = models.IntegerField(default=22, verbose_name='SSH 端口')
    ssh_user = models.CharField(max_length=50, default='root', verbose_name='SSH 用户')
    cpu = models.CharField(max_length=50, null=True, blank=True, verbose_name='CPU')
    memory = models.CharField(max_length=50, null=True, blank=True, verbose_name='内存')
    disk = models.CharField(max_length=50, null=True, blank=True, verbose_name='磁盘')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='online', verbose_name='状态')
    business_line = models.ForeignKey(
        'BusinessLine',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='所属业务线'
    )
    cluster = models.ForeignKey(
        'Cluster',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='所属集群'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'host'
        verbose_name = '主机'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return f"{self.hostname}({self.ip_address})"


class BusinessLine(models.Model):
    """业务线模型（兼容旧版）.

    本模块已升级为统一 Asset 模型，此 BusinessLine 模型保留用于兼容现有引用。
    新代码请使用 BusinessServiceNode 模型。
    """

    name = models.CharField(max_length=100, verbose_name='业务线名称')
    description = models.TextField(null=True, blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'business_line'
        verbose_name = '业务线'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.name


class Environment(models.Model):
    """环境模型（兼容旧版）.

    本模块已升级为统一 Asset 模型，此 Environment 模型保留用于兼容现有引用。
    """

    name = models.CharField(max_length=50, verbose_name='环境名称')
    code = models.CharField(max_length=20, unique=True, verbose_name='环境代码')
    description = models.TextField(null=True, blank=True, verbose_name='描述')
    sort_order = models.IntegerField(default=0, verbose_name='排序')

    class Meta:
        db_table = 'environment'
        verbose_name = '环境'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.name


class Application(models.Model):
    """应用模型（兼容旧版）.

    本模块已升级为统一 Asset 模型，此 Application 模型保留用于兼容现有引用。
    """

    name = models.CharField(max_length=100, verbose_name='应用名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='应用代码')
    description = models.TextField(null=True, blank=True, verbose_name='描述')
    business_line = models.ForeignKey(
        BusinessLine,
        on_delete=models.CASCADE,
        verbose_name='所属业务线'
    )
    owner = models.CharField(max_length=100, null=True, blank=True, verbose_name='负责人')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        db_table = 'application'
        verbose_name = '应用'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        return self.name


class Cluster(models.Model):
    """集群模型（兼容旧版）.

    本模块已升级为统一 Asset 模型，此 Cluster 模型保留用于兼容现有引用。
    """

    name = models.CharField(max_length=100, verbose_name='集群名称')
    code = models.CharField(max_length=50, unique=True, verbose_name='集群代码')
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        verbose_name='所属应用'
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        verbose_name='所属环境'
    )
    description = models.TextField(null=True, blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'cluster'
        verbose_name = '集群'
        verbose_name_plural = verbose_name
        unique_together = ['application', 'environment', 'code']

    def __str__(self) -> str:
        return f"{self.application.name}/{self.environment.code}/{self.code}"


class ApplicationDependency(models.Model):
    """应用依赖关系模型（兼容旧版）.

    本模块已升级为统一 Asset 模型，此 ApplicationDependency 模型保留用于兼容现有引用。
    新代码请使用 Relationship 模型。
    """

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='dependencies',
        verbose_name='应用'
    )
    depends_on = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='dependents',
        verbose_name='依赖应用'
    )
    description = models.TextField(null=True, blank=True, verbose_name='依赖说明')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        db_table = 'application_dependency'
        verbose_name = '应用依赖'
        verbose_name_plural = verbose_name
        unique_together = ['application', 'depends_on']

    def __str__(self) -> str:
        return f"{self.application.code} -> {self.depends_on.code}"