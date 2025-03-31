from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from executor.logs import logger
from launcher.forms.launcher import LauncherForm
from manager.models.app import Runnable
from manager.models.token import retrieve_token
from ..cache.albums import retrieve_user_albums
from ..models import Submission
from ..tasks import retrieve_series, submit_jobs


def launcher_view(request: HttpRequest) -> HttpResponse:
    user = request.user
    user_id = user.username

    access_token = retrieve_token(user)
    if access_token is None:  # No valid token, logout and re-login user to have a new token
        logout(request)
        return redirect('/')

    if request.method == 'POST':
        form = LauncherForm(access_token, user_id, request.POST)
        form.fields['albums'].choices = [(album.id_, album.label) for album in retrieve_user_albums(access_token, user_id)]

        if form.is_valid():
            runnable: Runnable = form.cleaned_data['runnables']
            album_id = form.cleaned_data['albums']
            study_date_filter = form.cleaned_data['study_date']
            study_date_filter = '*' if study_date_filter == '' else study_date_filter

            series_description_filter = form.cleaned_data['series_description']
            series_description_filter = '*' if series_description_filter == '' else series_description_filter

            # Once the user submit the code, mark as to-be submitted
            submission = Submission.objects.create(user=request.user, submitted=False)

            submit_jobs.apply_async(
                kwargs={
                    'user_id': user_id,
                    'submission_pk': submission.pk,
                    'album_id': album_id,
                    'access_token': access_token,
                    'modality': runnable.modality.abbreviation,
                    'app_name': runnable.app.name,
                    'app_version': runnable.version,
                    'study_date_filter': study_date_filter,
                    'series_description_filter': series_description_filter
                },
                priority=4
            )

            messages.add_message(
                request=request,
                level=messages.SUCCESS,
                message='The Jobs have been submitted! This may take a while before you see results in your album.'
            )

            return redirect('submissions')
    else:
        form = LauncherForm(access_token, user_id)

    return TemplateResponse(request, 'forms/launcher.html', {'form': form})


def find_number_of_series_that_fits_view(request: HttpRequest) -> HttpResponse:
    try:
        runnable = Runnable.objects.filter(id=request.POST['runnables']).first()
        album_id = request.POST['albums']

        study_date_filter = request.POST['study_date']
        study_date_filter = '*' if study_date_filter == '' else study_date_filter

        series_description_filter = request.POST['series_description']
        series_description_filter = '*' if series_description_filter == '' else series_description_filter

    except (IndexError, ValueError):
        return HttpResponse('Missing value.')

    access_token = retrieve_token(request.user)
    if access_token is None:  # No valid token, logout and re-login user to have a new token
        logout(request)
        return redirect('/')

    try:
        series_in_album = retrieve_series(
            album_id=album_id,
            access_token=access_token,
            modality=runnable.modality.abbreviation,
            study_date_filter=study_date_filter,
            series_description_filter=series_description_filter
        )
    except Exception:
        logger.exception('Failed to retrieve series.')
        return HttpResponse('error')

    return HttpResponse(len(series_in_album))
