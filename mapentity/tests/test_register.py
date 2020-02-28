from django.contrib.gis.db import models
from django.test import TestCase

from mapentity.registry import registry
from mapentity.models import MapEntityMixin


from geotrek.diving.models import Dive


class ModelDoNotExist(MapEntityMixin, models.Model):
    pass


class RegistryTest(TestCase):
    def test_already_register(self):
        paterns = registry.register(model=Dive, menu=False)
        self.assertEqual(paterns, [])
