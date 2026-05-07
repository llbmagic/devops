from django.db import models


class BusinessLine(models.Model):
    name = models.CharField(max_length=100, verbose_name='业务线名称')
    description = models.TextField(null=True, blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'business_line'
        verbose_name = '业务线'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class Tag(models.Model):
    key = models.CharField(max_length=50, verbose_name='标签键')
    value = models.CharField(max_length=100, verbose_name='标签值')

    class Meta:
        db_table = 'tag'
        verbose_name = '标签'
        verbose_name_plural = verbose_name
        unique_together = ['key', 'value']

    def __str__(self):
        return f"{self.key}:{self.value}"


class Host(models.Model):
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
    business_line = models.ForeignKey(BusinessLine, null=True, on_delete=models.SET_NULL, verbose_name='所属业务线')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='标签')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'host'
        verbose_name = '主机'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.hostname}({self.ip_address})"