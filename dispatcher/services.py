from executor.executor import setup_and_submit_slurm_job
from manager.models import Job, Runnable
from manager.serializers import JobWithoutConstraintValidationSerializer
from .log import logger


def submit_job(modality: str,
               series_instance_uid: str,
               study_instance_uid: str,
               album_id: str = None,
               app_name: str = None,
               app_version: str = None) -> list[Job]:
    logger.debug(f'Reading runnables with {series_instance_uid=}, {study_instance_uid=}, {album_id=}, {app_name=}, {app_version=}')
    runnables = Runnable.objects.select_related('app').filter(modality__abbreviation=modality, is_active=True)

    if album_id and app_name and app_version:
        runnables = runnables.filter(app__name=app_name, version=app_version)

        if not runnables.exists():
            logger.error(f"No runnables found for {app_name=} {app_version=}")
            raise ValueError(f"No runnables found for {app_name=} {app_version=}")

    elif album_id or app_name or app_version:
        logger.error(f"Can't publish message to AMQPC. One of these missing: {album_id=}, {app_name=}, {app_version=}")
        raise ValueError(
            f"Can't publish message to AMQPC. One of these missing: {album_id=}, {app_name=}, {app_version=}"
        )

    else:
        # When no target album and specific runnable, only the runnables that is mark as `automatic_run` will be used.
        # The other must be trigger manually.
        runnables = list(runnables.filter(app__automatic_run=True))

        runnables = _find_highest_version_of_each_application(runnables)

    jobs = _prepare_jobs_before_submit_to_queue(runnables, series_instance_uid, study_instance_uid, album_id)

    for job in jobs:
        job_data = JobWithoutConstraintValidationSerializer(job).data
        setup_and_submit_slurm_job.apply_async(
            kwargs={'job_data': job_data},
            priority=5
        )

    return jobs


def _find_highest_version_of_each_application(runnables: list[Runnable]) -> list[Runnable]:
    runnables_grouped_by_app = _group_runnables_by_app(runnables)

    return [_find_highest_version(runnable) for runnable in runnables_grouped_by_app.values()]


def _find_highest_version(runnables: list[Runnable]) -> Runnable:
    return max(runnables, key=_find_major_minor_patch)


def _group_runnables_by_app(runnables: list[Runnable]) -> dict[str, list[Runnable]]:
    """Returns runnable grouped by app name {'app1': [Runnable1, Runnable2], 'app2': [Runnable3]}"""
    grouped_runnables = {runnable.app.name: [] for runnable in runnables}

    for runnable in runnables:
        grouped_runnables[runnable.app.name].append(runnable)

    return grouped_runnables


def _find_major_minor_patch(runnable: Runnable) -> tuple[int, int, int]:
    major, minor, patch = runnable.version.split('.')

    return int(major), int(minor), int(patch)


def _prepare_jobs_before_submit_to_queue(
        runnables: list[Runnable],
        series_instance_uid: str,
        study_instance_uid: str,
        album_id: str | None) -> list[Job]:
    return [
        _get_or_create_job(
            study_instance_uid=study_instance_uid,
            series_instance_uid=series_instance_uid,
            runnable=runnable,
            kheops_album_id=album_id
        ) for runnable in runnables
    ]


def _get_or_create_job(study_instance_uid: str, series_instance_uid: str, runnable: Runnable, kheops_album_id: str) -> Job:
    job = Job.objects.filter(series_instance_uid=series_instance_uid, runnable=runnable).first()

    if job is None:
        return Job.objects.create(
            study_instance_uid=study_instance_uid,
            series_instance_uid=series_instance_uid,
            slurm_id=None,
            runnable=runnable,
            state=Job.State.SUBMITTED_TO_QUEUE,
            kheops_album_id=kheops_album_id
        )

    return job
