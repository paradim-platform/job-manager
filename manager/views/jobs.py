from rest_framework.generics import get_object_or_404
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from .. import models, serializers


class JobsViewSet(ModelViewSet):
    queryset = models.Job.objects.all()
    serializer_class = serializers.JobSerializer

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        return Response({'jobs': response.data})

    def get_object(self) -> models.Job:
        """Override the get_object method since we query a Job with runnable information"""
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, **self.kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj
