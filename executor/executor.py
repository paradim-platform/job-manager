import io
import os
import pathlib
import re
import shutil
import tempfile
import zipfile

import pyorthanc

from job_manager.celery import app
from launcher.kheops import client_api as kheops_client_api
from manager.models import GeneratedSeries, Job, Level
from manager.serializers import JobWithoutConstraintValidationSerializer
from . import kheops, orthanc, schedulers, ssh
from .config import PARADIM_TOKEN, SLURM_USER_NAME
from .errors import ParsingError
from .logs import logger

TEMPLATE_SLURM_JOB_PATH = pathlib.Path(__file__).parent.resolve() / 'templates/slurm.job'
DIST_DIRNAME = f'/home/{SLURM_USER_NAME}/data'


@app.task(ignore_result=True)
def setup_and_submit_slurm_job(job_data: dict) -> None:
    logger.debug(f'setup_and_submit_slurm_job called with {job_data=}')
    job_serializer = JobWithoutConstraintValidationSerializer(data=job_data)

    if job_serializer.is_valid():
        job = Job.objects.get(**job_serializer.validated_data)
    else:
        logger.error(f'Validation error: {job_serializer.errors}')
        return

    if not job.runnable.is_active:
        logger.info(f'{job} is inactive. Skipping.')
        job.state = Job.State.CANCELLED
        job.save()
        return

    generated_seriess = GeneratedSeries.objects.filter(
        job__runnable__app__name=job.runnable.app.name,
        job__runnable__version=job.runnable.version,
        job__series_instance_uid=job.series_instance_uid,
    )

    if job.state == Job.State.FINISHED:
        if job.kheops_album_id is not None:
            logger.info(f'{job} exists, copying corresponding results to album {job.kheops_album_id}.')
            for generated_series in generated_seriess:
                if generated_series.is_technical_sr is False:
                    kheops.client.copy_series_to_target_album(generated_series.series_instance_uid, job.kheops_album_id)
        else:
            logger.info(f'{job} exists, but no target album has been provided. Skipping.')

    elif job.state == Job.State.APP_ERROR:
        logger.info(f'{job} failed since app {job.runnable} raised an error. Skipping.')

    elif job.state in [Job.State.SUBMITTED_TO_QUEUE, Job.State.TECHNICAL_ERROR, Job.State.CANCELLED]:
        logger.debug(f'Submit {job} to Slurm...')
        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                logger.info('Setup and submit job')
                logger.debug(f'Job value : {job}')
                _prepare_job(job, tmp_dir)
                _send_job_files(job, tmp_dir)
                _submit_slurm_job(job)

            logger.debug(f'Submit {job} to Slurm... Done')

        except Exception as e:
            # Sometime something goes wrong above, if it's the case, requeue.
            logger.error(f'Submit {job} to Slurm... Failed, retrying. Error: {str(e)}')
            # Retry jobs
            setup_and_submit_slurm_job.apply_async(args=[job_data], priority=4, countdown=300)  # 5 mins delay, with higher priority

        if job.kheops_album_id is not None:
            # Re-submitting to Queue the job after submitting to SLURM so that when the job will be FINISHED,
            # the result will be added to the target album.
            setup_and_submit_slurm_job.apply_async(args=[job_data], priority=2, countdown=300)  # 5 mins delay, with higher priority

    elif job.state in [Job.State.RUNNING, Job.State.SUBMITTED_TO_SLURM]:
        # Since the job state is running or submitted to slurm,
        # Resubmit it until a result/error happens
        logger.debug(f'{job} has already been submitted to Slurm or is running. Re-queuing...')
        setup_and_submit_slurm_job.apply_async(args=[job_data], priority=2, countdown=300)  # 5 mins delay, with higher priority

    else:
        raise NotImplementedError(f'job State {job.state} not handled.')


def _prepare_job(job: Job, tmp_directory: str) -> None:
    _pull_data(job, tmp_directory)
    _setup_slurm_template(job, tmp_directory)


def _pull_data(job: Job, tmp_directory: str) -> None:
    series_list = pyorthanc.find_series(
        query={'SeriesInstanceUID': job.series_instance_uid},
        client=orthanc.client
    )

    if len(series_list) != 1:
        raise ValueError(
            f'{len(series_list)} series "{job.series_instance_uid}" found in Orthanc (should only have one).'
        )

    if job.runnable.level.value == Level.SERIES:
        logger.info(f'Pulling data (Series) from Orthanc ({series_list[0]}).')
        series_list[0].download(f'{tmp_directory}/{job.zip_filename}')

    elif job.runnable.level.value == Level.STUDY:
        logger.info(f'Pulling data (Study) from Orthanc ({series_list[0]}).')
        study = pyorthanc.Study(id_=series_list[0].study_identifier, client=orthanc.client)

        # Filter series in Study to only keep the series in the album (the ones that the user is allowed to see)
        kheops_series_uids = [s.uid for s in kheops_client_api.get_series_in_album(job.kheops_album_id)]

        # Download all allowed series
        tmp_study_dir = f'{tmp_directory}/study_dir'
        for series in study.series:
            if series.uid in kheops_series_uids:
                # Prepare Series directory
                series_modality = series.modality
                tmp_series_dir = f'{tmp_study_dir}/{series.uid}'
                os.makedirs(tmp_series_dir, exist_ok=True)

                # Download and extract
                with tempfile.TemporaryDirectory() as tmp_dir_for_series_zip:
                    series.download(f'{tmp_dir_for_series_zip}/series.zip')

                    with zipfile.ZipFile(f'{tmp_dir_for_series_zip}/series.zip', 'r') as zip_ref:
                        for i, name in enumerate(zip_ref.namelist()):
                            # Read a specific DICOM file in zip
                            with zip_ref.open(name) as dcm_file:
                                dcm_bytes = dcm_file.read()

                            # Write the DICOM file
                            with open(f'{tmp_series_dir}/{series_modality}{i}.dcm', 'wb') as file:
                                file.write(dcm_bytes)

        # Zip the allowed series
        # NOTE: `make_archive` put a .zip at the end of the filename. We need to use `.replace(".zip", "")`
        shutil.make_archive(f'{tmp_directory}/{job.zip_filename.replace(".zip", "")}', 'zip', tmp_study_dir)

    else:
        logger.error(f'Failed to pull data from Orthanc because of level={job.runnable.level.value}.')
        raise NotImplementedError()


def _setup_slurm_template(job: Job, tmp_directory: str) -> None:
    slurm_file = schedulers.make_slurm_file(job, DIST_DIRNAME, PARADIM_TOKEN)

    with open(f'{tmp_directory}/{job.job_filename}', 'w') as file:
        file.write(slurm_file)


def _send_job_files(job: Job, tmp_directory: str) -> None:
    with ssh.client.as_sftp() as sftp:
        sftp.put(f'{tmp_directory}/{job.zip_filename}', f'{DIST_DIRNAME}/{job.zip_filename}')
        sftp.put(f'{tmp_directory}/{job.job_filename}', f'{DIST_DIRNAME}/{job.job_filename}')


def _submit_slurm_job(job: Job) -> None:
    job_filepath = f'{DIST_DIRNAME}/{job.job_filename}'

    with ssh.client.as_ssh() as ssh_client:
        stdin, stdout, stderr = ssh_client.exec_command(f'sbatch {job_filepath}')

        output = stdout.read().decode()
        slurm_id_match = re.search(r'Submitted batch job (\d+)', output)
        if slurm_id_match is None:
            raise ParsingError(
                f'Failed to parse Slurm file for {job}, stdout: {output}, stderr: {stderr.read().decode()}'
            )

        job.slurm_id = slurm_id_match.group(1)
        job.state = Job.State.SUBMITTED_TO_SLURM
        job.save()
