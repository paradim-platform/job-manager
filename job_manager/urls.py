from urllib.parse import urlencode

from django.contrib import admin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import include, path, reverse
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import serializers, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .admin import admin_cache_management_view, clear_cache


class HealthCheckAPIView(APIView):

    @extend_schema(
        operation_id='Health check',
        responses={
            status.HTTP_200_OK: inline_serializer(
                name='health',
                fields={'status': serializers.CharField(default='ok')}
            )
        },
    )
    def get(self, request: Request):
        return Response({'status': 'ok'}, status=status.HTTP_200_OK)


def redirect_to_launcher(request: HttpRequest) -> HttpResponse:
    url = reverse('launcher')

    return HttpResponseRedirect(f'{url}?{urlencode(request.GET)}')


urlpatterns = [
    path('health/', HealthCheckAPIView.as_view(), name='health'),
    path('dispatcher/', include('dispatcher.urls')),
    path('admin/cache-management/', admin_cache_management_view, name='admin-cache-management'),
    path('admin/cache-management/clear', clear_cache, name='admin-cache-management-clear'),
    path('admin/', admin.site.urls),
    path('launcher/', include('launcher.urls')),
    path('manager/', include('manager.urls')),
    path('', redirect_to_launcher, name='index'),
]
