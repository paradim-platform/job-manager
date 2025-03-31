from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from .. import models, serializers


class RunnablesAPIView(GenericAPIView):
    queryset = models.Runnable.objects.filter(is_active=True)
    serializer_class = serializers.RunnablesSerializer

    @extend_schema(
        operation_id='Get runnables',
        responses={200: serializers.RunnablesSerializer},
        parameters=[
            OpenApiParameter(
                name='modality',
                description='Query runnables with given modality',
                required=False,
                type=str
            )
        ]
    )
    def get(self, request: Request) -> Response:
        modality = self.request.query_params.get('modality')
        qs = self.get_queryset().order_by('app__name', '-version')

        if modality is not None:
            qs = qs.filter(modality__abbreviation=modality)

        serializer = self.get_serializer({'runnables': qs})

        return Response(serializer.data)
