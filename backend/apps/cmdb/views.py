from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import BusinessLine, Tag, Host
from .serializers import BusinessLineSerializer, TagSerializer, HostSerializer


class BusinessLineViewSet(viewsets.ModelViewSet):
    queryset = BusinessLine.objects.all()
    serializer_class = BusinessLineSerializer


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.select_related('business_line').prefetch_related('tags').all()
    serializer_class = HostSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        business_line = self.request.query_params.get('business_line')
        status = self.request.query_params.get('status')
        if business_line:
            queryset = queryset.filter(business_line_id=business_line)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

    @action(detail=True, methods=['post'])
    def update_tags(self, request, pk=None):
        host = self.get_object()
        tag_ids = request.data.get('tag_ids', [])
        host.tags.set(tag_ids)
        return Response({'status': 'ok'})

    @action(detail=False, methods=['post'])
    def batch_update_tags(self, request):
        host_ids = request.data.get('host_ids', [])
        tag_ids = request.data.get('tag_ids', [])
        Host.objects.filter(id__in=host_ids).update(tags=tag_ids)
        return Response({'status': 'ok'})