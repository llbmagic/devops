from rest_framework import serializers
from .models import JenkinsInstance, JenkinsJob, BuildRecord, Pipeline


class JenkinsInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = JenkinsInstance
        fields = '__all__'
        extra_kwargs = {'api_token': {'write_only': True}}


class JenkinsJobSerializer(serializers.ModelSerializer):
    instance_name = serializers.CharField(source='instance.name', read_only=True)

    class Meta:
        model = JenkinsJob
        fields = '__all__'


class BuildRecordSerializer(serializers.ModelSerializer):
    job_name = serializers.CharField(source='job.name', read_only=True)

    class Meta:
        model = BuildRecord
        fields = '__all__'
        read_only_fields = ['id', 'started_at']


class PipelineSerializer(serializers.ModelSerializer):
    job_name = serializers.CharField(source='job.name', read_only=True)

    class Meta:
        model = Pipeline
        fields = '__all__'
