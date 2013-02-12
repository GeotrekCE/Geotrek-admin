from operator import attrgetter

from django.test import TestCase
from django.db import IntegrityError

from ..models import Trek
from ..factories import TrekFactory, TrekRelationshipFactory
from caminae.core.factories import PathFactory


class TrekTestCase(TestCase):

    def test_relationships(self):
        trek1 = TrekFactory()
        trek2 = TrekFactory()
        trek3 = TrekFactory()

        rs_12 = TrekRelationshipFactory(trek_a=trek1, trek_b=trek2)
        rs_23 = TrekRelationshipFactory(trek_a=trek2, trek_b=trek3)

        self.assertItemsEqual(trek1.related.all(), [ trek2 ])
        self.assertItemsEqual(trek2.related.all(), [ trek1, trek3 ])
        self.assertItemsEqual(trek3.related.all(), [ trek2 ])

    def test_relationship_insertion(self):
        trek1 = TrekFactory()
        trek2 = TrekFactory()
        TrekRelationshipFactory(trek_a=trek1, trek_b=trek2)
        # This should fail, since it already exists
        self.assertRaises(IntegrityError, lambda: TrekRelationshipFactory(trek_a=trek2, trek_b=trek1))

    def test_relationship_auto(self):
        trek1 = TrekFactory(departure="Labelle")
        trek2 = TrekFactory(departure="Labelle")
        self.assertItemsEqual(trek1.related.all(), [ trek2 ])

        p1 = PathFactory.create()
        p2 = PathFactory.create()
        p3 = PathFactory.create()
        trek3 = TrekFactory.create(no_path=True)
        trek3.add_path(p1)
        trek3.add_path(p2)
        trek3.save()
        trek4 = TrekFactory.create(no_path=True)
        trek4.add_path(p2)
        trek4.add_path(p3)
        trek4.save()
        print trek3.related.all()
        self.assertItemsEqual(trek3.related.all(), [ trek4 ])
