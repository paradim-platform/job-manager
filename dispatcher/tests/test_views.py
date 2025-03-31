from http import HTTPStatus
from unittest import mock

from django.urls import reverse
from rest_framework.test import APITestCase

from manager import models as manager_models


class HealthCheckTest(APITestCase):

    def test_health(self):
        response = self.client.get(reverse('health'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), {'status': 'ok'})


class JobsTest(APITestCase):

    def setUp(self):
        app1 = manager_models.App.objects.create(name='Algo1', description='DESCRIPTION')
        app2 = manager_models.App.objects.create(name='Algo2', description='DESCRIPTION', automatic_run=True)

        modality = manager_models.Modality.objects.create(abbreviation='CT', long_name='Computed Tomography',
                                                          is_active=True)
        level = manager_models.Level.objects.create(value=manager_models.Level.SERIES)
        size = manager_models.Size.objects.create(abbreviation=manager_models.Size.S)

        self.runnables = [
            manager_models.Runnable.objects.create(
                app=app1, modality=modality, version='1.12.3',
                level=level, with_gpu=False, size=size, is_active=True
            ),
            manager_models.Runnable.objects.create(
                app=app1, modality=modality, version='1.12.4',
                level=level, with_gpu=False, size=size, is_active=True
            ),
            manager_models.Runnable.objects.create(
                app=app2, modality=modality, version='2.3.0',
                level=level, with_gpu=False, size=size, is_active=True
            ),
        ]

    @mock.patch('dispatcher.services.setup_and_submit_slurm_job.apply_async')
    def test_jobs(self, mock_setup_and_submit_mock: mock.Mock):
        response = self.client.post(
            path=reverse('jobs'),
            data={'modality': 'CT', 'series_instance_uid': 'SERIES_INSTANCE_UID',
                  'study_instance_uid': 'STUDY_INSTANCE_UID'}
        )

        mock_setup_and_submit_mock.assert_called_once()  # Only Algo2 is in automatic run
        self.assertEqual(response.status_code, HTTPStatus.ACCEPTED)
        self.assertEqual(response.json(), {'status': 'published'})

    @mock.patch('dispatcher.services.setup_and_submit_slurm_job.apply_async')
    def test_jobs_optional(self, _: mock.Mock):
        response = self.client.post(
            path=reverse('jobs'),
            data={
                'modality': 'CT',
                'series_instance_uid': 'SERIES_INSTANCE_UID',
                'study_instance_uid': 'STUDY_INSTANCE_UID',
                'album_id': 'ALBUM_ID',
                'app_name': 'Algo1',
                'app_version': '1.12.3'
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.ACCEPTED)
        self.assertEqual(response.json(), {'status': 'published'})

    def test_jobs_bad_format(self):
        response = self.client.post(path=reverse('jobs'), data={'bad_format': 'CT'})

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                'modality': ['This field is required.'],
                'series_instance_uid': ['This field is required.'],
                'study_instance_uid': ['This field is required.'],
            }
        )

    def test_jobs_missing_one_optional(self):
        response = self.client.post(
            path=reverse('jobs'),
            data={
                'modality': 'CT',
                'series_instance_uid': 'SERIES_INSTANCE_UID',
                'study_instance_uid': 'STUDY_INSTANCE_UID',
                'album_id': 'ALBUM_ID',
                'app_name': 'APP_NAME',
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                'error': "Can't publish message to AMQPC. "
                         "One of these missing: album_id='ALBUM_ID', app_name='APP_NAME', app_version=None"
            })

    def test_jobs_non_existing_runnable(self):
        response = self.client.post(
            path=reverse('jobs'),
            data={
                'modality': 'CT',
                'series_instance_uid': 'SERIES_INSTANCE_UID',
                'study_instance_uid': 'STUDY_INSTANCE_UID',
                'album_id': 'ALBUM_ID',
                'app_name': 'APP_NAME',
                'app_version': 'APP_VERSION',
            }
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
        self.assertEqual(
            response.json(),
            {
                'error': "No runnables found for app_name='APP_NAME' app_version='APP_VERSION'"
            })
