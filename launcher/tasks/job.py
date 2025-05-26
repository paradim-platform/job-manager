from dispatcher.services import submit_job
from job_manager.celery import app
from launcher.models import Submission
from launcher.tasks.utils import retrieve_series


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
