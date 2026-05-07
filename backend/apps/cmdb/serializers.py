from rest_framework import serializers
from .models import BusinessLine, Tag, Host


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class BusinessLineSerializer(serializers.ModelSerializer):
    host_count = serializers.SerializerMethodField()

    class Meta:
        model = BusinessLine
        fields = '__all__'

    def get_host_count(self, obj):
        return obj.host_set.count()


class HostSerializer(serializers.ModelSerializer):
    business_line_name = serializers.CharField(source='business_line.name', read_only=True)
    tags_detail = TagSerializer(source='tags', many=True, read_only=True)

    class Meta:
        model = Host
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']