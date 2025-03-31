from django.urls import path

from .views.generated_series import GeneratedSeriesListCreateAPIView
from .views.jobs import JobsViewSet
from .views.runnables import RunnablesAPIView

urlpatterns = [
    path('runnables/', RunnablesAPIView.as_view(), name='runnables'),
    path('jobs/', JobsViewSet.as_view({'get': 'list'}), name='jobs-list'),
    path(
        route='jobs/<str:runnable__app__name>/<str:runnable__version>/<str:series_instance_uid>/',
        view=JobsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update'}),
        name='jobs-detail'
    ),
    path('generated-series/', GeneratedSeriesListCreateAPIView.as_view(), name='generated-series-list-create'),
]
