from unittest import TestCase

from manager.models import App, Level, Modality, Runnable, Size
from ..services import _find_highest_version_of_each_application


class FindHighestVersionOfEachApplication(TestCase):

    def setUp(self) -> None:
        app1 = App(name='app1', description='DESCRIPTION1')
        app2 = App(name='app2', description='DESCRIPTION2')
        modality = Modality(abbreviation='CT')
        size = Size(abbreviation='S')
        level = Level(value='Series')
        self.runnable1_highest = Runnable(app=app1, version='1.12.2', level=level, modality=modality, size=size)
        self.runnable2_highest = Runnable(app=app2, version='1.13.1', level=level, modality=modality, size=size)
        self.runnables = [
            Runnable(app=app1, version='1.12.1', level=level, modality=modality, size=size),
            self.runnable1_highest,
            Runnable(app=app1, version='1.11.1', level=level, modality=modality, size=size),
            Runnable(app=app2, version='1.11.1', level=level, modality=modality, size=size),
            self.runnable2_highest,
        ]

    def test_find_highest_version_of_each_application(self):
        result = _find_highest_version_of_each_application(self.runnables)

        self.assertEqual(len(result), 2)
        self.assertIn(self.runnable1_highest, result)
        self.assertIn(self.runnable2_highest, result)
