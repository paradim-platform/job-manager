import unittest
from http import HTTPStatus

from django.urls import reverse
from parameterized import parameterized

from ... import models
from ..setup import APITestCaseWithRunnable

JOB_ID = 999
OTHER_JOB_ID = 12345
JOB_STATE = models.Job.State.SUBMITTED_TO_SLURM
APP_NAME = 'Algo1'
APP_VERSION = '1.12.3'
SERIES_INSTANCE_UID = '1.123.12345.123.1234.12444433837987389'
STUDY_INSTANCE_UID = '1.123.12345.123.1234.987654321987654321'
GENERATED_SERIES_INSTANCE_UID = '1.123.12345.123.1234.987654321'


class JobsTest(APITestCaseWithRunnable):
    def setUp(self) -> None:
        super().setUp()
        self.job = models.Job.objects.create(slurm_id=JOB_ID, series_instance_uid=SERIES_INSTANCE_UID, study_instance_uid=STUDY_INSTANCE_UID, state=JOB_STATE, runnable=self.runnable)

    def test_get_job(self):
        response = self.client.get(
            reverse('jobs-detail', args=[self.runnable.app.name, self.runnable.version, SERIES_INSTANCE_UID])
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {
            'slurm_id': self.job.slurm_id,
            'state': self.job.state,
            'series_instance_uid': self.job.series_instance_uid,
            'study_instance_uid': self.job.study_instance_uid,
            'generated_series_instance_uids': [],
            'app_info': {
                'name': self.job.runnable.app.name,
                'version': self.job.runnable.version
            }
        })

    def test_get_job_error(self):
        response = self.client.get(
            reverse('jobs-detail', args=[self.runnable.app.name, 'NOT_EXISTING_VERSION', SERIES_INSTANCE_UID])
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_update_job(self):
        response = self.client.put(
            path=reverse('jobs-detail', args=[self.job.runnable.app.name, self.job.runnable.version, SERIES_INSTANCE_UID]),
            data={
                'slurm_id': self.job.slurm_id,
                'series_instance_uid': self.job.series_instance_uid,
                'study_instance_uid': self.job.study_instance_uid,
                'state': models.Job.State.RUNNING,
                'app_info': {'name': self.job.runnable.app.name, 'version': self.job.runnable.version}
            },
            format='json'
        )

        self.job.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.job.state, models.Job.State.RUNNING)

    def test_update_job_errors(self):
        # Missing field
        response = self.client.put(
            path=reverse('jobs-detail', args=[self.job.runnable.app.name, self.job.runnable.version, SERIES_INSTANCE_UID]),
            data={'slurm_id': self.job.slurm_id, 'state': models.Job.State.RUNNING},
            format='json'
        )

        self.job.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(response.json(), {'app_info': ['This field is required.'], 'series_instance_uid': ['This field is required.'], 'study_instance_uid': ['This field is required.']})
        self.assertEqual(self.job.state, models.Job.State.SUBMITTED_TO_SLURM)

        # Non-existing Job
        response = self.client.put(
            path=reverse('jobs-detail', args=[self.job.runnable.app.name, self.job.runnable.version, 'NOT_EXISTING_SERIES_UID']),
            data={
                'slurm_id': self.job.slurm_id,
                'state': models.Job.State.RUNNING,
                'app_info': {'name': self.job.runnable.app.name, 'version': self.job.runnable.version}
            },
            format='json'
        )

        self.job.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(response.json(), {'detail': 'No Job matches the given query.'})
        self.assertEqual(self.job.state, models.Job.State.SUBMITTED_TO_SLURM)

    def test_partial_update_job(self):
        response = self.client.patch(
            path=reverse('jobs-detail', args=[self.job.runnable.app.name, self.job.runnable.version, SERIES_INSTANCE_UID]),
            data={'state': models.Job.State.RUNNING},
        )

        self.job.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(self.job.state, models.Job.State.RUNNING)

    def test_partial_update_job_errors(self):
        response = self.client.patch(
            path=reverse('jobs-detail', args=[self.job.runnable.app.name, self.job.runnable.version, 'NOT_EXISTING_SERIES_UID']),
            data={'state': models.Job.State.RUNNING},
        )

        self.job.refresh_from_db()
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(self.job.state, models.Job.State.SUBMITTED_TO_SLURM)


class JobsListCreateTest(APITestCaseWithRunnable):

    def test_list_jobs_without_jobs(self):
        response = self.client.get(path=reverse('jobs-list'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {'jobs': []})

    def test_list_jobs(self):
        job = models.Job.objects.create(slurm_id=JOB_ID, series_instance_uid=SERIES_INSTANCE_UID, study_instance_uid=STUDY_INSTANCE_UID, state=JOB_STATE, runnable=self.runnable)
        models.GeneratedSeries.objects.create(job=job, series_instance_uid=GENERATED_SERIES_INSTANCE_UID)

        response = self.client.get(path=reverse('jobs-list'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json(),
            {
                'jobs': [
                    {
                        'app_info': {'name': 'Algo1', 'version': '1.12.3'},
                        'generated_series_instance_uids': [GENERATED_SERIES_INSTANCE_UID],
                        'series_instance_uid': SERIES_INSTANCE_UID,
                        'study_instance_uid': STUDY_INSTANCE_UID,
                        'slurm_id': 999,
                        'state': 'SUBMITTED_TO_SLURM',
                    }
                ]
            }
        )

    @unittest.skip('Job creation deactivated because dispatcher now use the django ORM (Was used before because dispatcher and manager were microservices).')
    def test_create_job(self):
        self.assertFalse(models.Job.objects.exists())

        response = self.client.post(
            path=reverse('jobs-list'),
            data={
                'slurm_id': JOB_ID,
                'series_instance_uid': SERIES_INSTANCE_UID,
                'study_instance_uid': STUDY_INSTANCE_UID,
                'state': JOB_STATE,
                'app_info': {'name': APP_NAME, 'version': APP_VERSION}
            },
            format='json'
        )

        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.json())
        self.assertTrue(models.Job.objects.exists())
        job = models.Job.objects.all().first()
        self.assertEqual(job.slurm_id, JOB_ID)
        self.assertEqual(job.state, JOB_STATE)

    @parameterized.expand([
        (
                {'slurm_id': 'not-an-int', 'series_instance_uid': SERIES_INSTANCE_UID, 'study_instance_uid': STUDY_INSTANCE_UID, 'state': JOB_STATE, 'app_info': {'name': APP_NAME, 'version': APP_VERSION}},
                HTTPStatus.BAD_REQUEST,
                {'slurm_id': ['A valid integer is required.']}
        ),
        (
                {'slurm_id': JOB_ID, 'series_instance_uid': SERIES_INSTANCE_UID, 'study_instance_uid': STUDY_INSTANCE_UID, 'state': 'bad-state', 'app_info': {'name': APP_NAME, 'version': APP_VERSION}},
                HTTPStatus.BAD_REQUEST,
                {'state': ['"bad-state" is not a valid choice.']}
        ),
        (
                {'slurm_id': JOB_ID, 'series_instance_uid': SERIES_INSTANCE_UID, 'study_instance_uid': STUDY_INSTANCE_UID, 'state': JOB_STATE, 'app_info': {'name': APP_NAME, 'version': '0.0.0'}},
                HTTPStatus.BAD_REQUEST,
                {'app_info': ['Runnable not find for name=Algo1, version=0.0.0']}
        ),
    ])
    @unittest.skip('Job creation deactivated because dispatcher now use the django ORM (Was used before because dispatcher and manager were microservices).')
    def test_create_job_bad_request(self, data, expected_status: int, expected_message: str):
        response = self.client.post(
            path=reverse('jobs-list'),
            data=data,
            format='json'
        )

        self.assertEqual(response.status_code, expected_status)
        self.assertEqual(response.json(), expected_message)

    @unittest.skip('Job creation deactivated because dispatcher now use the django ORM (Was used before because dispatcher and manager were microservices).')
    def test_create_same_job_twice(self):
        self.assertFalse(models.Job.objects.exists())

        # First create
        response = self.client.post(
            path=reverse('jobs-list'),
            data={
                'slurm_id': JOB_ID,
                'series_instance_uid': SERIES_INSTANCE_UID,
                'study_instance_uid': STUDY_INSTANCE_UID,
                'state': JOB_STATE,
                'app_info': {'name': APP_NAME, 'version': APP_VERSION}
            },
            format='json'
        )

        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.json())
        self.assertTrue(models.Job.objects.exists())
        job = models.Job.objects.all().first()
        self.assertEqual(job.slurm_id, JOB_ID)
        self.assertEqual(job.state, JOB_STATE)

        # Create again with same slurm_id
        response = self.client.post(
            path=reverse('jobs-list'),
            data={
                'slurm_id': JOB_ID,
                'series_instance_uid': SERIES_INSTANCE_UID,
                'study_instance_uid': STUDY_INSTANCE_UID,
                'state': JOB_STATE,
                'app_info': {'name': APP_NAME, 'version': APP_VERSION}
            },
            format='json'
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.json())
        self.assertEqual(response.json(), {'slurm_id': ['job with this slurm id already exists.']})

        # Create again with different slurm_id
        response = self.client.post(
            path=reverse('jobs-list'),
            data={
                'slurm_id': OTHER_JOB_ID,
                'series_instance_uid': SERIES_INSTANCE_UID,
                'study_instance_uid': STUDY_INSTANCE_UID,
                'state': JOB_STATE,
                'app_info': {'name': APP_NAME, 'version': APP_VERSION}
            },
            format='json'
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST, response.json())
        self.assertEqual(response.json(), [f"This Job already exists {{'slurm_id': 12345, 'state': 'SUBMITTED', 'series_instance_uid': '{SERIES_INSTANCE_UID}', 'study_instance_uid': '{STUDY_INSTANCE_UID}'}}"])
