from http import HTTPStatus

from django.urls import reverse

from ..setup import APITestCaseWithRunnable


class RunnablesTest(APITestCaseWithRunnable):

    def test_runnables_all(self):
        response = self.client.get(reverse('runnables'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json(),
            {
                'runnables': [
                    {
                        'app': 'Algo1',
                        'version': '1.12.4',
                        'level': 'Series',
                        'modality': 'PET',
                        'size': 'S',
                        'with_gpu': False
                    },
                    {
                        'app': 'Algo1',
                        'version': '1.12.3',
                        'level': 'Series',
                        'modality': 'CT',
                        'size': 'S',
                        'with_gpu': False
                    }
                ]
            }
        )

    def test_runnables_for_given_modality(self):
        response = self.client.get(reverse('runnables') + '?modality=CT')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(
            response.json(),
            {
                'runnables': [
                    {
                        'app': 'Algo1',
                        'version': '1.12.3',
                        'level': 'Series',
                        'modality': 'CT',
                        'size': 'S',
                        'with_gpu': False
                    }
                ]
            }
        )
