from django.test import TestCase
from django.db import IntegrityError
from django.db.models import Q

from ..factories import TrekFactory, TrekRelationshipFactory
from ..models import TrekRelationship


class TrekRelationshipsTestCase(TestCase):

    def setUp(self):
        self.trek1 = TrekFactory(name="1")
        self.trek2 = TrekFactory(name="2")
        self.trek3 = TrekFactory(name="3")
        TrekRelationshipFactory(trek_a=self.trek1, trek_b=self.trek2)
        TrekRelationshipFactory(trek_a=self.trek2, trek_b=self.trek3)

    def test_related_treks_symetries(self):
        self.assertItemsEqual(self.trek1.related.all(), [self.trek2])
        self.assertItemsEqual(self.trek2.related.all(), [self.trek1, self.trek3])
        self.assertItemsEqual(self.trek3.related.all(), [self.trek2])

    def test_symetrical_relationships(self):
        relations_1 = TrekRelationship.objects.filter(Q(trek_a=self.trek1) | Q(trek_b=self.trek1))
        relations_2 = TrekRelationship.objects.filter(Q(trek_a=self.trek2) | Q(trek_b=self.trek2))
        relations_3 = TrekRelationship.objects.filter(Q(trek_a=self.trek3) | Q(trek_b=self.trek3))
        self.assertEqual(len(relations_1), 2)
        self.assertEqual(len(relations_2), 4)
        self.assertEqual(len(relations_3), 2)

    def test_relationship_fails_if_duplicate(self):
        # This should fail, since it already exists
        def create_dup():
            return TrekRelationshipFactory(trek_a=self.trek2, trek_b=self.trek1)
        self.assertRaises(IntegrityError, create_dup)
