from django.test import TestCase
from operator import attrgetter

from ..factories import TrekFactory, TrekRelationshipFactory


# Helpers to extract pk from objects
get_pk = attrgetter('pk')
get_pks = lambda l: [get_pk(i) for i in l]


class TrekTestCase(TestCase):

    def test_helper_methods(self):
        """
        Test that helper methods `get_related_treks_values` and
        `get_relationships` works.
        """

        trek1 = TrekFactory()
        trek2 = TrekFactory()
        trek3 = TrekFactory()

        rs_12 = TrekRelationshipFactory(trek_a=trek1, trek_b=trek2)
        rs_23 = TrekRelationshipFactory(trek_a=trek2, trek_b=trek3)

        self.assertItemsEqual(trek1.get_related_treks_values(), [ trek2 ])
        self.assertItemsEqual(trek2.get_related_treks_values(), [ trek1, trek3 ])
        self.assertItemsEqual(trek3.get_related_treks_values(), [ trek2 ])

        self.assertQuerysetEqual(
                trek1.get_relationships(), get_pks([ rs_12 ]), get_pk)
        self.assertQuerysetEqual(
                trek2.get_relationships(), get_pks([ rs_12, rs_23 ]), get_pk)
        self.assertQuerysetEqual(
                trek3.get_relationships(), get_pks([ rs_23 ]), get_pk)

    # TODO: this should fail ! And it does not !
    def test_relationship_insertion(self):
        """
        Demonstrate that our current Trek relationship implementation has
        serious limitation:
        we should only allow one link between trekA and trekB.
        """

        trek1 = TrekFactory()
        trek2 = TrekFactory()

        # We should allow _only one_ link between two treks
        # How ? Reordering on pk ..? Don't know
        TrekRelationshipFactory(trek_a=trek1, trek_b=trek2)
        TrekRelationshipFactory(trek_a=trek2, trek_b=trek1)


