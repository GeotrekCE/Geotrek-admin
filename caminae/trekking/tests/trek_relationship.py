from django.test import TestCase
from django.db import IntegrityError

from ..factories import TrekFactory, TrekRelationshipFactory
from caminae.core.factories import PathFactory


class TrekRelationshipsTestCase(TestCase):

    def test_relationships(self):
        trek1 = TrekFactory()
        trek2 = TrekFactory()
        trek3 = TrekFactory()

        rs_12 = TrekRelationshipFactory(trek_a=trek1, trek_b=trek2)
        rs_23 = TrekRelationshipFactory(trek_a=trek2, trek_b=trek3)

        self.assertItemsEqual(trek1.related.all(), [trek2])
        self.assertItemsEqual(trek2.related.all(), [trek1, trek3])
        self.assertItemsEqual(trek3.related.all(), [trek2])

    def test_relationship_insertion(self):
        trek1 = TrekFactory()
        trek2 = TrekFactory()
        TrekRelationshipFactory(trek_a=trek1, trek_b=trek2)
        # This should fail, since it already exists
        self.assertRaises(IntegrityError, lambda: TrekRelationshipFactory(trek_a=trek2, trek_b=trek1))
