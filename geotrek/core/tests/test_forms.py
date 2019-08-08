from django.conf import settings
from django.test import TestCase

from unittest import skipIf

from geotrek.core.factories import TrailFactory
from geotrek.authent.factories import UserFactory
from geotrek.core.forms import TrailForm


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class TopologyFormTest(TestCase):
    def test_save_form_when_topology_has_not_changed(self):
        user = UserFactory()
        topo = TrailFactory()
        form = TrailForm(instance=topo, user=user)
        self.assertEqual(topo, form.instance)
        form.cleaned_data = {'topology': topo}
        form.save()
        self.assertEqual(topo, form.instance)
