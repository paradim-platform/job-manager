from django.urls import path

from .views import JobsAPIView

urlpatterns = [
    path('jobs/', JobsAPIView.as_view(), name='jobs'),
]
