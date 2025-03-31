from rest_framework.test import APITestCase

from .. import models


class APITestCaseWithRunnable(APITestCase):

    def setUp(self) -> None:
        modality = models.Modality.objects.create(abbreviation='CT', long_name='TOMO')
        level = models.Level.objects.create(value=models.Level.SERIES)
        app = models.App.objects.create(name='Algo1', description='This is very cool')
        size = models.Size.objects.create(abbreviation=models.Size.S)
        self.runnable = models.Runnable.objects.create(app=app, modality=modality, version='1.12.3', level=level, size=size)

        other_modality = models.Modality.objects.create(abbreviation='PET', long_name='PET Scanc')
        self.other_runnable = models.Runnable.objects.create(
            app=app, modality=other_modality, version='1.12.4', level=level, size=size
        )
