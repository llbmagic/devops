from django.db import models

class JenkinsInstance(models.Model):
    name = models.CharField(max_length=100, verbose_name='实例名称')
    url = models.URLField(verbose_name='Jenkins URL')
    username = models.CharField(max_length=100, verbose_name='用户名')
    api_token = models.CharField(max_length=200, verbose_name='API Token')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')

    class Meta:
        db_table = 'jenkins_instance'
        verbose_name = 'Jenkins 实例'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class JenkinsJob(models.Model):
    INSTANCE_TYPE_CHOICES = [
        ('jenkins', 'Jenkins'),
    ]
    instance = models.ForeignKey(JenkinsInstance, on_delete=models.CASCADE, verbose_name='所属实例')
    name = models.CharField(max_length=200, verbose_name='Job 名称')
    job_url = models.URLField(verbose_name='Job URL', blank=True)
    last_build_number = models.IntegerField(default=0, verbose_name='最后构建号')
    last_build_status = models.CharField(max_length=20, null=True, blank=True, verbose_name='最后构建状态')
    last_build_time = models.DateTimeField(null=True, blank=True, verbose_name='最后构建时间')

    class Meta:
        db_table = 'jenkins_job'
        verbose_name = 'Jenkins Job'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.instance.name}/{self.name}"


class BuildRecord(models.Model):
    STATUS_CHOICES = [
        ('pending', '排队中'),
        ('running', '运行中'),
        ('success', '成功'),
        ('failure', '失败'),
        ('aborted', '中止'),
    ]
    job = models.ForeignKey(JenkinsJob, on_delete=models.CASCADE, related_name='builds', verbose_name='Job')
    build_number = models.IntegerField(verbose_name='构建号')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    duration = models.IntegerField(null=True, blank=True, verbose_name='持续时间(秒)')
    executor = models.CharField(max_length=100, null=True, blank=True, verbose_name='执行人')
    commit_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='提交ID')
    log_url = models.URLField(null=True, blank=True, verbose_name='日志URL')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    finished_at = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')

    class Meta:
        db_table = 'build_record'
        verbose_name = '构建记录'
        verbose_name_plural = verbose_name
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.job.name} #{self.build_number}"


class Pipeline(models.Model):
    name = models.CharField(max_length=100, verbose_name='流水线名称')
    job = models.ForeignKey(JenkinsJob, on_delete=models.CASCADE, verbose_name='关联 Job')
    target_hosts = models.ManyToManyField('cmdb.Host', blank=True, verbose_name='目标主机')
    description = models.TextField(null=True, blank=True, verbose_name='描述')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'pipeline'
        verbose_name = '流水线'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name
