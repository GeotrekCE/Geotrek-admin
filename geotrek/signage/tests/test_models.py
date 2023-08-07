from django.contrib.auth.models import User
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from geotrek.authent.tests.factories import UserFactory
from geotrek.signage.models import Blade
from geotrek.signage.tests.factories import BladeFactory, BladeTypeFactory, SealingFactory, SignageFactory
from geotrek.infrastructure.tests.factories import InfrastructureFactory


class SealingModelTest(TestCase):
    def test_sealing_value(self):
        sealing = SealingFactory.create(label='sealing_1', structure=None)
        self.assertEqual(str(sealing), 'sealing_1')


class BladeTypeModelTest(TestCase):
    def test_bladetype_value(self):
        type = BladeTypeFactory.create(label='type_1', structure=None)
        self.assertEqual(str(type), 'type_1')


class BladeModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = User.objects.filter(username="__internal__")
        if not user:
            UserFactory(username="__internal__")

    def test_set_topology_other_error(self):
        blade = BladeFactory.create()
        infra = InfrastructureFactory.create()
        with self.assertRaisesRegex(ValueError, "Expecting a signage"):
            blade.set_topology(infra)

    def test_cascading_deletions(self):
        blade = BladeFactory.create()
        topo_pk = blade.topology.pk
        topo_repr = str(blade.topology)
        blade.topology.delete(force=True)
        blade_model_num = ContentType.objects.get_for_model(Blade).pk
        blade_entry = LogEntry.objects.get(content_type=blade_model_num, object_id=blade.pk)
        self.assertEqual(blade_entry.change_message, f"Deleted by cascade from Topology {topo_pk} - {topo_repr}")
        self.assertEqual(blade_entry.action_flag, DELETION)
        signa = SignageFactory()
        blade = BladeFactory(signage=signa)
        signa_pk = signa.pk
        signa_repr = str(signa)
        # NoDeleteMixin
        signa.delete()
        self.assertTrue(blade.delete)
        # Force through NoDeleteMixin
        signa.delete(force=True)
        blade_model_num = ContentType.objects.get_for_model(Blade).pk
        blade_entry = LogEntry.objects.get(content_type=blade_model_num, object_id=blade.pk)
        self.assertEqual(blade_entry.change_message, f"Deleted by cascade from Signage {signa_pk} - {signa_repr}")
        self.assertEqual(blade_entry.action_flag, DELETION)


class SignageModelTest(TestCase):
    def test_order_blades_C(self):
        signage = SignageFactory.create(code="XR2")
        blade_2 = BladeFactory.create(number='A', signage=signage)
        blade = BladeFactory.create(number='*BL', signage=signage)
        self.assertEqual([blade, blade_2], list(signage.order_blades))
