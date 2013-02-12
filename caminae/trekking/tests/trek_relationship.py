from operator import attrgetter

from django.test import TestCase
from django.db import IntegrityError

from ..models import Trek
from ..factories import TrekFactory, TrekRelationshipFactory


class TrekTestCase(TestCase):

    def test_relationships(self):
        trek1 = TrekFactory()
        trek2 = TrekFactory()
        trek3 = TrekFactory()

        rs_12 = TrekRelationshipFactory(trek_a=trek1, trek_b=trek2)
        rs_23 = TrekRelationshipFactory(trek_a=trek2, trek_b=trek3)

        self.assertItemsEqual(trek1.related_treks.all(), [ trek2 ])
        self.assertItemsEqual(trek2.related_treks.all(), [ trek1, trek3 ])
        self.assertItemsEqual(trek3.related_treks.all(), [ trek2 ])

    def test_relationship_insertion(self):
        trek1 = TrekFactory()
        trek2 = TrekFactory()
        TrekRelationshipFactory(trek_a=trek1, trek_b=trek2)
        # This should fail, since it already exists
        self.assertRaises(IntegrityError, lambda: TrekRelationshipFactory(trek_a=trek2, trek_b=trek1))


