from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from geotrek.authent.tests.factories import StructureFactory, UserFactory
from geotrek.infrastructure.tests.factories import InfrastructureFactory
from geotrek.signage.models import Blade
from geotrek.signage.tests.factories import (
    BladeConditionFactory,
    BladeFactory,
    BladeTypeFactory,
    LinePictogramFactory,
    SealingFactory,
    SignageConditionFactory,
    SignageFactory,
    SignageTypeNoPictogramFactory,
)


class SealingModelTest(TestCase):
    def test_sealing_value(self):
        sealing = SealingFactory.create(label="sealing_1", structure=None)
        self.assertEqual(str(sealing), "sealing_1")


class BladeTypeModelTest(TestCase):
    def test_bladetype_value(self):
        type = BladeTypeFactory.create(label="type_1", structure=None)
        self.assertEqual(str(type), "type_1")


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
        blade_entry = LogEntry.objects.get(
            content_type=blade_model_num, object_id=blade.pk
        )
        self.assertEqual(
            blade_entry.change_message,
            f"Deleted by cascade from Topology {topo_pk} - {topo_repr}",
        )
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
        blade_entry = LogEntry.objects.get(
            content_type=blade_model_num, object_id=blade.pk
        )
        self.assertEqual(
            blade_entry.change_message,
            f"Deleted by cascade from Signage {signa_pk} - {signa_repr}",
        )
        self.assertEqual(blade_entry.action_flag, DELETION)

    def test_str_bladecondition_with_structure(self):
        structure = StructureFactory(name="This")
        bladecondition = BladeConditionFactory(label="condition", structure=structure)
        self.assertEqual(str(bladecondition), f"condition ({structure.name})")

    def test_str_bladecondition_without_structure(self):
        bladecondition = BladeConditionFactory(label="condition", structure=None)
        self.assertEqual(str(bladecondition), "condition")


class SignageModelTest(TestCase):
    def test_order_blades_C(self):
        signage = SignageFactory.create(code="XR2")
        blade_2 = BladeFactory.create(number="A", signage=signage)
        blade = BladeFactory.create(number="*BL", signage=signage)
        self.assertEqual([blade, blade_2], list(signage.order_blades))

    def test_str_signagecondition_with_structure(self):
        structure = StructureFactory(name="This")
        signagecondition = SignageConditionFactory(
            label="condition", structure=structure
        )
        self.assertEqual(str(signagecondition), f"condition ({structure.name})")

    def test_str_signagecondition_without_structure(self):
        signagecondition = SignageConditionFactory(label="condition", structure=None)
        self.assertEqual(str(signagecondition), "condition")


class LinePictogramModelTest(TestCase):
    def test_str_linepictogram(self):
        linepictogram = LinePictogramFactory(label="fresnais")
        self.assertEqual(str(linepictogram), "fresnais")


class SignageTypeTestCase(TestCase):
    def test_pictogram_url_default(self):
        """Return signage type default pictogram if not defined"""
        signage_type = SignageTypeNoPictogramFactory()
        self.assertEqual(
            signage_type.get_pictogram_url(), "/static/signage/picto-signage.png"
        )
