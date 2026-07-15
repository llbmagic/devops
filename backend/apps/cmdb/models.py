"""CMDB 资产管理模块.

提供运维平台的核心资产数据模型，包括业务线、环境、应用、集群、主机等
资产管理功能，支撑 2000+ 主机的统一纳管。

数据模型层次结构:
    业务线 (BusinessLine)
        └── 应用 (Application)
              └── 集群 (Cluster)
                    └── 主机 (Host)

其他模型:
    - Tag: 标签，用于主机多维度分类
    - ApplicationDependency: 应用依赖关系

典型使用场景:
    - 按业务线统计主机数量
    - 按环境和应用组织集群
    - 追踪应用间依赖关系
    - 主机标签化管理

示例:
    >>> from apps.cmdb.models import BusinessLine, Host
    >>> bl = BusinessLine.objects.create(name='电商平台')
    >>> Host.objects.create(hostname='web-01', ip_address='192.168.1.1', business_line=bl)
"""

from django.db import models


class BusinessLine(models.Model):
    """业务线模型.

    业务线是资产的顶层分类，用于区分不同业务部门或产品线。
    每个业务线可以包含多个应用和主机。

    属性:
        name: 业务线名称，最长 100 个字符。
        description: 业务线描述，可选。
        created_at: 创建时间，自动设置。

    示例:
        >>> BusinessLine.objects.create(name='电商平台', description='公司电商业务')
    """

    name = models.CharField(
        max_length=100,
        verbose_name='业务线名称',
        help_text='业务线的显示名称'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='业务线的详细描述'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'business_line'，Django Admin 显示为"业务线"。
        """
        db_table = 'business_line'
        verbose_name = '业务线'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回业务线的字符串表示.

        Returns:
            业务线名称。
        """
        return self.name


class Environment(models.Model):
    """环境模型.

    表示软件部署的不同环境，典型环境包括开发、测试、预发布、生产等。
    环境与集群是多对多关系（通过 Cluster 模型关联）。

    属性:
        name: 环境名称，如"开发环境"。
        code: 环境代码，唯一标识，如 dev/test/staging/prod。
        description: 环境描述，可选。
        sort_order: 排序序号，用于控制环境列表的显示顺序。

    示例:
        >>> Environment.objects.create(name='开发环境', code='dev', sort_order=1)
        >>> Environment.objects.create(name='生产环境', code='prod', sort_order=99)
    """

    name = models.CharField(
        max_length=50,
        verbose_name='环境名称',
        help_text='环境的显示名称，如"开发环境"'
    )
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='环境代码',
        help_text='唯一标识代码，如 dev/test/staging/prod'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='环境的详细描述'
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name='排序',
        help_text='用于控制列表显示顺序，数值越小越靠前'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'environment'，按 sort_order 和 id 排序。
        """
        db_table = 'environment'
        verbose_name = '环境'
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        """返回环境的字符串表示.

        Returns:
            环境名称。
        """
        return self.name


class Application(models.Model):
    """应用模型.

    应用是业务线的子集，代表一个具体的业务应用或服务。
    应用下辖多个集群，每个集群对应特定环境和部署配置。

    属性:
        name: 应用名称，如"用户服务"。
        code: 应用代码，唯一标识，如 user-service。
        description: 应用描述，可选。
        business_line: 所属业务线，外键关联。
        owner: 应用负责人，可选。
        created_at: 创建时间，自动设置。
        updated_at: 更新时间，自动更新。

    示例:
        >>> from apps.cmdb.models import BusinessLine
        >>> bl = BusinessLine.objects.get(code='ecommerce')
        >>> Application.objects.create(
        ...     name='用户服务',
        ...     code='user-service',
        ...     business_line=bl,
        ...     owner='张三'
        ... )
    """

    name = models.CharField(
        max_length=100,
        verbose_name='应用名称',
        help_text='应用的显示名称'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='应用代码',
        help_text='唯一标识代码，用于 API 和关联'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='应用的详细描述'
    )
    business_line = models.ForeignKey(
        BusinessLine,
        on_delete=models.CASCADE,
        verbose_name='所属业务线',
        help_text='应用所属的业务线'
    )
    owner = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='负责人',
        help_text='应用负责人姓名'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'application'。
        """
        db_table = 'application'
        verbose_name = '应用'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回应用的字符串表示.

        Returns:
            应用名称。
        """
        return self.name


class Cluster(models.Model):
    """集群模型.

    集群是应用在特定环境下的部署实例，代表一组相同配置的主机。
    集群与应用是多对一关系，与环境也是多对一关系。
    同一应用在同一环境下不能有重复代码的集群。

    属性:
        name: 集群名称，如"用户服务-Dev集群"。
        code: 集群代码，唯一标识，如 user-dev。
        application: 所属应用，外键关联。
        environment: 所属环境，外键关联。
        description: 集群描述，可选。
        created_at: 创建时间，自动设置。

    示例:
        >>> from apps.cmdb.models import Application, Environment
        >>> app = Application.objects.get(code='user-service')
        >>> env = Environment.objects.get(code='dev')
        >>> Cluster.objects.create(
        ...     name='用户服务-Dev集群',
        ...     code='user-dev',
        ...     application=app,
        ...     environment=env
        ... )
    """

    name = models.CharField(
        max_length=100,
        verbose_name='集群名称',
        help_text='集群的显示名称'
    )
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='集群代码',
        help_text='唯一标识代码'
    )
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        verbose_name='所属应用',
        help_text='集群所属的应用'
    )
    environment = models.ForeignKey(
        Environment,
        on_delete=models.CASCADE,
        verbose_name='所属环境',
        help_text='集群所属的环境'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='描述',
        help_text='集群的详细描述'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'cluster'。
        同一应用同一环境下 code 必须唯一。
        """
        db_table = 'cluster'
        verbose_name = '集群'
        verbose_name_plural = verbose_name
        unique_together = ['application', 'environment', 'code']

    def __str__(self) -> str:
        """返回集群的字符串表示.

        Returns:
            格式为"应用名/环境码/集群码"的字符串。
        """
        return f"{self.application.name}/{self.environment.code}/{self.code}"


class Tag(models.Model):
    """标签模型.

    标签是主机的多维度分类标记，支持 key-value 形式。
    标签用于主机的灵活分组，如按用途、技术栈、负责人等维度标记。

    属性:
        key: 标签键，如 env、os、purpose。
        value: 标签值，如 python、linux、web。

    注意:
        key-value 组合必须唯一，即同一 key 不能有重复的 value。

    示例:
        >>> Tag.objects.create(key='env', value='prod')
        >>> Tag.objects.create(key='os', value='linux')
    """

    key = models.CharField(
        max_length=50,
        verbose_name='标签键',
        help_text='标签的键，如 env、os、purpose'
    )
    value = models.CharField(
        max_length=100,
        verbose_name='标签值',
        help_text='标签的值'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'tag'。
        key-value 组合唯一。
        """
        db_table = 'tag'
        verbose_name = '标签'
        verbose_name_plural = verbose_name
        unique_together = ['key', 'value']

    def __str__(self) -> str:
        """返回标签的字符串表示.

        Returns:
            格式为"key:value"的字符串。
        """
        return f"{self.key}:{self.value}"


class Host(models.Model):
    """主机模型.

    主机是运维平台的核心资产，代表一台物理机或虚拟机。
    主机归属于业务线（可选）和集群（可选）。

    属性:
        hostname: 主机名，唯一标识，如 web-01。
        ip_address: IP 地址，支持 IPv4 和 IPv6。
        ssh_port: SSH 端口号，默认为 22。
        ssh_user: SSH 用户名，默认为 root。
        cpu: CPU 信息，可选。
        memory: 内存信息，可选。
        disk: 磁盘信息，可选。
        status: 主机状态，可选值包括 online/offline/maintenance。
        business_line: 所属业务线，外键关联，可选。
        cluster: 所属集群，外键关联，可选。
        tags: 主机标签，多对多关联。
        created_at: 创建时间，自动设置。
        updated_at: 更新时间，自动更新。

    状态说明:
        - online: 主机在线，运行正常
        - offline: 主机离线，可能宕机
        - maintenance: 主机维护中

    示例:
        >>> from apps.cmdb.models import BusinessLine, Cluster
        >>> bl = BusinessLine.objects.get(name='电商平台')
        >>> cluster = Cluster.objects.get(code='user-dev')
        >>> Host.objects.create(
        ...     hostname='web-01',
        ...     ip_address='192.168.1.101',
        ...     business_line=bl,
        ...     cluster=cluster,
        ...     status='online'
        ... )
    """

    STATUS_CHOICES = [
        ('online', '在线'),
        ('offline', '离线'),
        ('maintenance', '维护中'),
    ]

    hostname = models.CharField(
        max_length=100,
        verbose_name='主机名',
        help_text='主机的主机名或实例 ID'
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP 地址',
        help_text='主机的 IP 地址，支持 IPv4/IPv6'
    )
    ssh_port = models.IntegerField(
        default=22,
        verbose_name='SSH 端口',
        help_text='SSH 连接端口，默认为 22'
    )
    ssh_user = models.CharField(
        max_length=50,
        default='root',
        verbose_name='SSH 用户',
        help_text='SSH 连接用户名'
    )
    cpu = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='CPU',
        help_text='CPU 规格，如 8核'
    )
    memory = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='内存',
        help_text='内存规格，如 16GB'
    )
    disk = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name='磁盘',
        help_text='磁盘规格，如 500GB SSD'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='online',
        verbose_name='状态',
        help_text='主机状态：online-在线，offline-离线，maintenance-维护中'
    )
    business_line = models.ForeignKey(
        BusinessLine,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='所属业务线',
        help_text='主机所属的业务线'
    )
    cluster = models.ForeignKey(
        Cluster,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name='所属集群',
        help_text='主机所属的集群'
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        verbose_name='标签',
        help_text='主机的标签列表'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'host'。
        """
        db_table = 'host'
        verbose_name = '主机'
        verbose_name_plural = verbose_name

    def __str__(self) -> str:
        """返回主机的字符串表示.

        Returns:
            格式为"主机名(IP 地址)"的字符串。
        """
        return f"{self.hostname}({self.ip_address})"


class ApplicationDependency(models.Model):
    """应用依赖关系模型.

    记录应用之间的依赖关系，用于追踪服务调用链和影响分析。
    依赖关系是单向的，A 依赖 B 不代表 B 依赖 A。

    属性:
        application: 应用，外键关联，表示依赖方。
        depends_on: 被依赖的应用，外键关联。
        description: 依赖说明，可选，如 HTTP 调用、RPC 等。
        created_at: 创建时间，自动设置。

    注意:
        同一应用不能重复依赖同一个应用。

    示例:
        >>> from apps.cmdb.models import Application
        >>> user_svc = Application.objects.get(code='user-service')
        >>> pay_svc = Application.objects.get(code='payment-service')
        >>> ApplicationDependency.objects.create(
        ...     application=user_svc,
        ...     depends_on=pay_svc,
        ...     description='用户服务调用支付服务进行结算'
        ... )
    """

    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='dependencies',
        verbose_name='应用',
        help_text='依赖方应用'
    )
    depends_on = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='dependents',
        verbose_name='依赖应用',
        help_text='被依赖的应用'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='依赖说明',
        help_text='依赖关系的详细说明，如调用方式'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )

    class Meta:
        """模型元数据.

        数据库表名为 'application_dependency'。
        同一应用同一依赖应用组合唯一。
        """
        db_table = 'application_dependency'
        verbose_name = '应用依赖'
        verbose_name_plural = verbose_name
        unique_together = ['application', 'depends_on']

    def __str__(self) -> str:
        """返回依赖关系的字符串表示.

        Returns:
            格式为"应用代码 -> 依赖应用代码"的字符串。
        """
        return f"{self.application.code} -> {self.depends_on.code}"
