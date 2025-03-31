from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from .. import models, serializers


class GeneratedSeriesListCreateAPIView(ListCreateAPIView):
    queryset = models.GeneratedSeries.objects.all()
    serializer_class = serializers.GeneratedSeriesSerializer

    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)

        return Response({'generated_series_instance_uids': response.data})
