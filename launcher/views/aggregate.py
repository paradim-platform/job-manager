from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound
from django.shortcuts import redirect, reverse
from django.template.response import TemplateResponse
from django.views.decorators.http import require_http_methods

from manager.models.token import retrieve_token
from ..cache.aggregation import init_aggregation_cache, retrieve_aggregation_results_cache
from ..cache.albums import retrieve_user_albums
from ..forms.aggregate import AggregateForm
from ..tasks import create_aggregation_file


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
            output_format = form.cleaned_data['output_format']
            series_description_filter = form.cleaned_data['series_description_filter']

            init_aggregation_cache(user_id, album_id, series_description_filter, output_format)

            create_aggregation_file.apply_async(
                kwargs={
                    'album_id': album_id,
                    'access_token': access_token,
                    'user_id': user_id,
                    'series_description_filter': series_description_filter,
                    'output_format': output_format
                },
                priority=4
            )

            return redirect('aggregate-results')

    else:
        form = AggregateForm(access_token, user_id)

    return TemplateResponse(request, 'forms/aggregate.html', {'form': form})


def aggregate_results_view(request: HttpRequest) -> HttpResponse:
    results = retrieve_aggregation_results_cache(request.user.username)

    return TemplateResponse(request, 'aggregate_results.html', {'results': results})


def aggregate_result_view(request: HttpRequest, result_key: str) -> HttpResponse:
    results = retrieve_aggregation_results_cache(request.user.username)

    data = results.get(result_key, None)

    if data is None or data == 'running':
        return HttpResponse(f"""
                {result_key} 
                <div id="spinner" class="spinner-border ml-2" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                """)

    return HttpResponse(f"""<a href="{reverse('aggregate-result-file', kwargs={'result_key': result_key})}">{result_key}</a>""")


def aggregate_result_file(request: HttpRequest, result_key: str) -> HttpResponse:
    results = retrieve_aggregation_results_cache(request.user.username)
    data = results.get(result_key, None)

    if data is None:
        return HttpResponseNotFound(request)

    response = HttpResponse(data.encode(), content_type='text/csv' if result_key[:-4] == '.csv' else 'text/plain')
    response['Content-Disposition'] = f'attachment; filename="{result_key}"'

    return response
