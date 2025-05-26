from django.urls import path

from launcher.views.aggregate import aggregate_result_file, aggregate_result_view, aggregate_results_view, aggregate_view
from launcher.views.job import job_detail_view, rerun_job_view
from launcher.views.launcher import find_number_of_series_that_fits_view, launcher_view
from launcher.views.submissions import submission_view, submissions_view

urlpatterns = [
    path('', launcher_view, name='launcher'),
    path('launcher/find-number-fit', find_number_of_series_that_fits_view, name='launcher-find-number-fit'),

    path('submissions/', submissions_view, name='submissions'),
    path('submissions/<str:submission_id>', submission_view, name='submissions-detail'),

    path('jobs/<str:job_id>', job_detail_view, name='jobs-details'),
    path('jobs/<str:job_id>/rerun/', rerun_job_view, name='jobs-rerun'),

    path('aggregate/', aggregate_view, name='aggregate'),
    path('aggregate/results', aggregate_results_view, name='aggregate-results'),
    path('aggregate/results/<str:aggregation_id>', aggregate_result_file, name='aggregate-result-file'),
    path('aggregate/results-button/<str:aggregation_id>', aggregate_result_view, name='aggregate-result-button'),
]
