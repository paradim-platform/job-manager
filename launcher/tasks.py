import json
from fnmatch import fnmatch

import pandas as pd
import pyorthanc

from dispatcher.services import submit_job
from executor import orthanc
from job_manager.celery import app
from . import kheops
from .cache.aggregation import retrieve_aggregation_result_cache, set_as_running, set_result
from .cache.albums import retrieve_user_albums
from .kheops import client_api
from .models import Submission


@app.task(ignore_result=True)
def submit_jobs(
        user_id: str,
        submission_pk: str,
        album_id: str,
        access_token: str,
        modality: str,
        app_name: str,
        app_version: str,
        study_date_filter: str | None = None,
        series_description_filter: str | None = None) -> None:
    seriess = retrieve_series(
        album_id=album_id,
        access_token=access_token,
        modality=modality,
        study_date_filter=study_date_filter,
        series_description_filter=series_description_filter
    )

    submission = Submission.objects.get(pk=submission_pk)
    for series in seriess:
        jobs = submit_job(
            album_id=album_id,
            modality=modality,
            series_instance_uid=series.uid,
            study_instance_uid=series.study.uid,
            app_name=app_name,
            app_version=app_version
        )

        for job in jobs:
            submission.jobs.add(job)

        submission.submitted = True
        submission.save()


def retrieve_series(
        album_id: str,
        access_token: str,
        modality: str,
        study_date_filter: str | None = None,
        series_description_filter: str | None = None) -> list[kheops.Series]:
    study_date_filter = '*' if study_date_filter is None else study_date_filter.replace('-', '')
    series_description_filter = '*' if series_description_filter is None else series_description_filter

    series_in_album = client_api.get_series_in_album(album_id, modality)

    return [
        s for s in series_in_album
        if (
                s.modality == modality and
                fnmatch(s.description, series_description_filter) and
                fnmatch(s.study.date, study_date_filter)
        )
    ]


@app.task(ignore_result=True)
def create_aggregation_file(
        album_id: str,
        access_token: str,
        user_id: str,
        series_description_filter: str,
        output_format: str) -> None:
    result = retrieve_aggregation_result_cache(user_id, album_id, series_description_filter, output_format)
    if result is not None:
        # Result already exists, skip
        return

    # Marking the file as running
    set_as_running(user_id, album_id, series_description_filter, output_format)

    seriess = retrieve_series(
        album_id=album_id,
        access_token=access_token,
        modality='SR',
        series_description_filter=f'{series_description_filter}*',
    )

    data = None
    for s in seriess:
        series = pyorthanc.find_series(orthanc.client, query={'SeriesInstanceUID': s.uid})[0]
        for instance in series.instances:
            ds = instance.get_pydicom()
            prediction_dict = json.loads(ds.ContentSequence[0].TextValue)

            # The CSV case is handled differently. It makes a dataframe,
            # while the json output_format only return the raw content.
            if output_format == 'csv':
                if not data:
                    data = {k: [v] for k, v in prediction_dict.items()}
                else:
                    for k, v in prediction_dict.items():
                        data[k].append(v)
            else:
                if not data:
                    data = [prediction_dict]
                else:
                    data.append(prediction_dict)

    if output_format == 'csv':
        if data:
            df = pd.DataFrame.from_dict(data=data, orient="index").T
        else:
            df = pd.DataFrame()  # Means that no series was found. Return an empty csv
        result = df.to_csv(header=True, index=False)

    else:
        result = json.dumps(data)

    set_result(user_id, album_id, series_description_filter, output_format, result)


def _find_album_label(album_id: str, access_token: str, user_id: str):
    for album in retrieve_user_albums(access_token, user_id):
        if album.id_ == album_id:
            return album.label

    raise ValueError(f'Album not found {album_id}')
