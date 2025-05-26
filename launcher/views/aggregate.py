from django.contrib.auth import logout
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, reverse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods

from manager.models import Runnable
from manager.models.token import retrieve_token
from ..cache.albums import retrieve_user_albums
from ..forms.aggregate import AggregateForm
from ..models import AggregationSubmission
from ..tasks.aggregate import create_aggregation_file


@require_http_methods(["GET", "POST"])
def aggregate_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    user_id = user.username

    access_token = retrieve_token(user)
    if access_token is None:  # No valid token, logout and re-login user to have a new token
        logout(request)
        return redirect('/')

    if request.method == 'POST':
        form = AggregateForm(access_token, user_id, request.POST)
        form.fields['album'].choices = [(album.id_, album.label) for album in retrieve_user_albums(access_token, user_id)]

        if form.is_valid():
            album_id = form.cleaned_data['album']
            series_description_filter = form.cleaned_data['series_description_filter']
            output_format = form.cleaned_data['output_format']
            runnable: Runnable = form.cleaned_data['runnable']

            aggregation = AggregationSubmission.objects.create(
                filetype=AggregationSubmission.FileType.CSV if output_format == 'csv' else AggregationSubmission.FileType.JSON,
                state=AggregationSubmission.State.SUBMITTED,
                user=user,
                runnable=runnable,
                album_id=album_id,
            )

            create_aggregation_file.apply_async(
                kwargs={
                    'aggregation_pk': aggregation.pk,
                    'access_token': access_token,
                    'series_description_filter': series_description_filter,
                },
                priority=4
            )

            return redirect('aggregate-results')

    else:
        form = AggregateForm(access_token, user_id)

    return TemplateResponse(request, 'forms/aggregate.html', {'form': form})


def aggregate_results_view(request: HttpRequest) -> HttpResponse:
    aggregations = AggregationSubmission.objects.filter(user=request.user).order_by('-created').defer('result')

    return TemplateResponse(request, 'aggregate_results.html', {'aggregations': aggregations})


def aggregate_result_view(request: HttpRequest, aggregation_id: str) -> HttpResponse:
    aggregations = AggregationSubmission.objects.filter(pk=aggregation_id, user=request.user)

    if not aggregations.exists():
        raise Http404()

    aggregation = aggregations.first()

    if aggregation.state in [AggregationSubmission.State.SUBMITTED, AggregationSubmission.State.RUNNING]:
        return HttpResponse(f"""
                {aggregation} 
                <div id="spinner" class="spinner-border ml-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                """)

    return HttpResponse(f"""<a href="{reverse('aggregate-result-file', kwargs={'aggregation_id': aggregation.id})}">{aggregation}</a>""")


def aggregate_result_file(request: HttpRequest, aggregation_id: str) -> HttpResponse:
    aggregations = AggregationSubmission.objects.filter(pk=aggregation_id, user=request.user)
    if not aggregations.exists():
        raise Http404()

    aggregation = aggregations.first()
    data = aggregation.result
    is_csv = aggregation.filetype == AggregationSubmission.FileType.CSV
    filename = f'{str(aggregation)}.csv' if is_csv else f'{str(aggregation)}.json'

    response = HttpResponse(data.encode(), content_type='text/csv' if is_csv else 'text/plain')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
