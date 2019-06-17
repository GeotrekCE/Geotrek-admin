from django.test import TestCase, tag

from geotrek.core.factories import TrailFactory
from geotrek.authent.factories import UserFactory
from geotrek.core.forms import TrailForm


@tag('dynamic_segmentation')
class TopologyFormTest(TestCase):
    def test_save_form_when_topology_has_not_changed(self):
        user = UserFactory()
        topo = TrailFactory()
        form = TrailForm(instance=topo, user=user)
        self.assertEqual(topo, form.instance)
        form.cleaned_data = {'topology': topo}
        form.save()
        self.assertEqual(topo, form.instance)
