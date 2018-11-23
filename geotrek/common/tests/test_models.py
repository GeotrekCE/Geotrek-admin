from geotrek.common.models import Theme
from django.core.files import File
from django.test import TestCase
import os


class ThemeModelTest(TestCase):
    def setUp(self):
        self.directory = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')
        self.files = [f for f in os.listdir(self.directory)]

    def test_pictogram(self):
        self.path = os.path.join(self.directory, 'picto.png')
        self.assertEqual(os.path.getsize(self.path), 6203)
        self.theme = Theme.objects.create()

        self.theme.pictogram = File(open(self.path))
        file = self.theme.pictogram_off
        path_off = os.path.join(self.directory, 'picto_off.png')
        self.assertEqual(os.path.getsize(path_off), 4069)
        self.assertEqual(file.name, path_off)

    def tearDown(self):
        for f in os.listdir(self.directory):
            if f not in self.files:
                os.remove(os.path.join(self.directory, f))
