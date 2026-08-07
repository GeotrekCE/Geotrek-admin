from django.core.exceptions import ValidationError
from django.test import TestCase

from geotrek.core.fields import TopologyField


class TopologyFieldTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.f = TopologyField()

    def test_validation_fails_if_null_is_submitted(self):
        self.assertRaises(ValidationError, self.f.clean, "null")
