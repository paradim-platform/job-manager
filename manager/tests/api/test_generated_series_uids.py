from http import HTTPStatus

from django.urls import reverse

from .test_jobs import GENERATED_SERIES_INSTANCE_UID, JOB_ID, JOB_STATE, SERIES_INSTANCE_UID
from ..setup import APITestCaseWithRunnable
from ... import models


class GeneratedSeriesInstanceUIDTest(APITestCaseWithRunnable):

    def setUp(self) -> None:
        super().setUp()
        self.job = models.Job.objects.create(slurm_id=JOB_ID, series_instance_uid=SERIES_INSTANCE_UID, state=JOB_STATE, runnable=self.runnable)

    def test_list_generated_series_instance_uids_without_generated_series(self):
        response = self.client.get(reverse('generated-series-list-create'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json(),
            {'generated_series_instance_uids': []}
        )

    def test_list_generated_series_instance_uids(self):
        models.GeneratedSeries.objects.create(job=self.job, series_instance_uid=GENERATED_SERIES_INSTANCE_UID)

        response = self.client.get(reverse('generated-series-list-create'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json(),
            {
                'generated_series_instance_uids': [
                    {
                        'job': {
                            'app_info': {
                                'name': 'Algo1',
                                'modality': 'CT',
                                'version': '1.12.3'
                            },
                            'is_technical_sr': False,
                            'source_series_instance_uid': '1.123.12345.123.1234.987654321'
                        },
                        'series_instance_uid': '1.123.12345.123.1234.987654321'
                    }
                ]
            }
        )

    def test_create_generated_series_instance_uids(self):
        self.assertFalse(models.GeneratedSeries.objects.exists())

        response = self.client.post(
            path=reverse('generated-series-list-create'),
            data={
                'source_series_instance_uid': SERIES_INSTANCE_UID,
                'series_instance_uid': GENERATED_SERIES_INSTANCE_UID,
                'app_info': {
                    'name': self.job.runnable.app.name,
                    'modality': 'CT',
                    'version': self.job.runnable.version
                }
            },
            format='json'
        )

        self.assertEqual(response.status_code, HTTPStatus.CREATED, response.json())
        self.assertTrue(models.Job.objects.exists())
