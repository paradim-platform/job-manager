from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from .log import logger
from .serializers import RunnableSerializer
from .services import submit_job


class JobsAPIView(GenericAPIView):
    serializer_class = RunnableSerializer

    @extend_schema(
        operation_id='Submit jobs',
        description='Submit a job to the message queue containing the information on the app to run and with which data',
        responses={
            status.HTTP_202_ACCEPTED: inline_serializer(
                name='accepted',
                fields={'status': serializers.CharField(default='published')}
            ),
            status.HTTP_400_BAD_REQUEST: dict,
        },
    )
    def post(self, request: Request):
        logger.debug(f'Received {request.data}')
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        try:
            submit_job(**serializer.validated_data)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': 'published'}, status=status.HTTP_202_ACCEPTED)
