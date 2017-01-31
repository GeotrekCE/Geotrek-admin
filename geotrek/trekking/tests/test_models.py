from django.test import TestCase
from django.contrib.gis.geos import (LineString, Polygon, MultiPolygon,
                                     MultiLineString)
from django.core.exceptions import ValidationError

from bs4 import BeautifulSoup

from geotrek.common.tests import TranslationResetMixin
from geotrek.core.factories import PathFactory, PathAggregationFactory
from geotrek.zoning.factories import DistrictFactory, CityFactory
from geotrek.trekking.factories import (POIFactory, TrekFactory,
                                        TrekWithPOIsFactory, ServiceFactory)
from geotrek.trekking.models import Trek, OrderedTrekChild


class TrekTest(TranslationResetMixin, TestCase):
    def test_is_publishable(self):
        t = TrekFactory.create()
        t.geom = LineString((0, 0), (1, 1))
        self.assertTrue(t.has_geom_valid())

        t.description_teaser = ''
        self.assertFalse(t.is_complete())
        self.assertFalse(t.is_publishable())
        t.description_teaser = 'ba'
        t.departure = 'zin'
        t.arrival = 'ga'
        self.assertTrue(t.is_complete())
        self.assertTrue(t.is_publishable())

        t.geom = MultiLineString([LineString((0, 0), (1, 1)), LineString((2, 2), (3, 3))])
        self.assertFalse(t.has_geom_valid())
        self.assertFalse(t.is_publishable())

    def test_any_published_property(self):
        t = TrekFactory.create(published=False)
        t.published_fr = False
        t.published_it = False
        t.save()
        self.assertFalse(t.any_published)
        t.published_it = True
        t.save()
        self.assertTrue(t.any_published)

    def test_published_status(self):
        t = TrekFactory.create(published=False)
        t.published_fr = False
        t.published_it = True
        t.save()
        self.assertEqual(t.published_status, [
            {'lang': 'en', 'language': 'English', 'status': False},
            {'lang': 'es', 'language': 'Spanish', 'status': False},
            {'lang': 'fr', 'language': 'French', 'status': False},
            {'lang': 'it', 'language': 'Italian', 'status': True}])

    def test_kml_coordinates_should_be_3d(self):
        trek = TrekWithPOIsFactory.create()
        kml = trek.kml()
        parsed = BeautifulSoup(kml)
        for placemark in parsed.findAll('placemark'):
            coordinates = placemark.find('coordinates')
            tuples = [s.split(',') for s in coordinates.string.split(' ')]
            self.assertTrue(all([len(i) == 3 for i in tuples]))

    def test_pois_types(self):
        trek = TrekWithPOIsFactory.create()
        type0 = trek.pois[0].type
        type1 = trek.pois[1].type
        self.assertEqual(2, len(trek.poi_types))
        self.assertIn(type0, trek.poi_types)
        self.assertIn(type1, trek.poi_types)

    def test_delete_cascade(self):
        p1 = PathFactory.create()
        p2 = PathFactory.create()
        t = TrekFactory.create(no_path=True)
        t.add_path(p1)
        t.add_path(p2)

        # Everything should be all right before delete
        self.assertTrue(t.published)
        self.assertFalse(t.deleted)
        self.assertEqual(t.aggregations.count(), 2)

        # When a path is deleted
        p1.delete()
        t = Trek.objects.get(pk=t.pk)
        self.assertFalse(t.published)
        self.assertFalse(t.deleted)
        self.assertEqual(t.aggregations.count(), 1)

        # Reset published status
        t.published = True
        t.save()

        # When all paths are deleted
        p2.delete()
        t = Trek.objects.get(pk=t.pk)
        self.assertFalse(t.published)
        self.assertTrue(t.deleted)
        self.assertEqual(t.aggregations.count(), 0)

    def test_treks_are_sorted_by_name(self):
        TrekFactory.create(name='Cb')
        TrekFactory.create(name='Ca')
        TrekFactory.create(name='A')
        TrekFactory.create(name='B')
        self.assertEqual([u'A', u'B', u'Ca', u'Cb'],
                         list(Trek.objects.all().values_list('name', flat=True)))

    def test_trek_itself_as_parent(self):
        """
        Test if a trek it is its own parent
        """
        trek1 = TrekFactory.create(name='trek1')
        OrderedTrekChild.objects.create(parent=trek1, child=trek1)
        self.assertRaisesMessage(ValidationError,
                                 u"Cannot use itself as child trek.",
                                 trek1.full_clean)


class TrekPublicationDateTest(TranslationResetMixin, TestCase):
    def setUp(self):
        self.trek = TrekFactory.create(published=False)

    def test_default_value_is_null(self):
        self.assertIsNone(self.trek.publication_date)

    def test_takes_current_date_when_published_becomes_true(self):
        self.trek.published = True
        self.trek.save()
        self.assertIsNotNone(self.trek.publication_date)

    def test_becomes_null_when_unpublished(self):
        self.test_takes_current_date_when_published_becomes_true()
        self.trek.published = False
        self.trek.save()
        self.assertIsNone(self.trek.publication_date)

    def test_date_is_not_updated_when_saved_again(self):
        import datetime
        self.test_takes_current_date_when_published_becomes_true()
        old_date = datetime.date(2003, 8, 6)
        self.trek.publication_date = old_date
        self.trek.save()
        self.assertEqual(self.trek.publication_date, old_date)


class RelatedObjectsTest(TranslationResetMixin, TestCase):
    def test_helpers(self):
        trek = TrekFactory.create(no_path=True)
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        p2 = PathFactory.create(geom=LineString((4, 4), (8, 8)))
        poi = POIFactory.create(no_path=True)
        service = ServiceFactory.create(no_path=True)
        service.type.practices.add(trek.practice)
        PathAggregationFactory.create(topo_object=trek, path=p1,
                                      start_position=0.5)
        PathAggregationFactory.create(topo_object=trek, path=p2)
        PathAggregationFactory.create(topo_object=poi, path=p1,
                                      start_position=0.6, end_position=0.6)
        PathAggregationFactory.create(topo_object=service, path=p1,
                                      start_position=0.7, end_position=0.7)
        # /!\ District are automatically linked to paths at DB level
        d1 = DistrictFactory.create(geom=MultiPolygon(
            Polygon(((-2, -2), (3, -2), (3, 3), (-2, 3), (-2, -2)))))

        # Ensure related objects are accessible
        self.assertItemsEqual(trek.pois, [poi])
        self.assertItemsEqual(trek.services, [service])
        self.assertItemsEqual(poi.treks, [trek])
        self.assertItemsEqual(service.treks, [trek])
        self.assertItemsEqual(trek.districts, [d1])

        # Ensure there is no duplicates
        PathAggregationFactory.create(topo_object=trek, path=p1,
                                      end_position=0.5)
        self.assertItemsEqual(trek.pois, [poi])
        self.assertItemsEqual(trek.services, [service])
        self.assertItemsEqual(poi.treks, [trek])
        self.assertItemsEqual(service.treks, [trek])

        d2 = DistrictFactory.create(geom=MultiPolygon(
            Polygon(((3, 3), (9, 3), (9, 9), (3, 9), (3, 3)))))
        self.assertItemsEqual(trek.districts, [d1, d2])

    def test_deleted_pois(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        trek = TrekFactory.create(no_path=True)
        trek.add_path(p1)
        poi = POIFactory.create(no_path=True)
        poi.add_path(p1, start=0.6, end=0.6)
        self.assertItemsEqual(trek.pois, [poi])
        poi.delete()
        self.assertItemsEqual(trek.pois, [])

    def test_deleted_services(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        trek = TrekFactory.create(no_path=True)
        trek.add_path(p1)
        service = ServiceFactory.create(no_path=True)
        service.type.practices.add(trek.practice)
        service.add_path(p1, start=0.6, end=0.6)
        self.assertItemsEqual(trek.services, [service])
        service.delete()
        self.assertItemsEqual(trek.services, [])

    def test_pois_should_be_ordered_by_progression(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        p2 = PathFactory.create(geom=LineString((4, 4), (8, 8)))
        self.trek = TrekFactory.create(no_path=True)
        self.trek.add_path(p1)
        self.trek.add_path(p2, order=1)

        self.trek_reverse = TrekFactory.create(no_path=True)
        self.trek_reverse.add_path(p2, start=0.8, end=0, order=0)
        self.trek_reverse.add_path(p1, start=1, end=0.2, order=1)

        self.poi1 = POIFactory.create(no_path=True)
        self.poi1.add_path(p1, start=0.8, end=0.8)
        self.poi2 = POIFactory.create(no_path=True)
        self.poi2.add_path(p1, start=0.3, end=0.3)
        self.poi3 = POIFactory.create(no_path=True)
        self.poi3.add_path(p2, start=0.5, end=0.5)

        pois = self.trek.pois
        self.assertEqual([self.poi2, self.poi1, self.poi3], list(pois))
        pois = self.trek_reverse.pois
        self.assertEqual([self.poi3, self.poi1, self.poi2], list(pois))

    def test_city_departure(self):
        trek = TrekFactory.create(no_path=True)
        p1 = PathFactory.create(geom=LineString((0, 0), (5, 5)))
        trek.add_path(p1)
        self.assertEqual(trek.city_departure, '')

        city1 = CityFactory.create(geom=MultiPolygon(Polygon(((-1, -1), (3, -1), (3, 3),
                                                              (-1, 3), (-1, -1)))))
        city2 = CityFactory.create(geom=MultiPolygon(Polygon(((3, 3), (9, 3), (9, 9),
                                                              (3, 9), (3, 3)))))
        self.assertEqual(list(trek.cities.values_list('pk', flat=True)), [city1.pk, city2.pk])
        self.assertEqual(trek.city_departure, unicode(city1))


class TrekUpdateGeomTest(TestCase):
    def setUp(self):
        self.trek = TrekFactory.create(published=True, geom=LineString(((700000, 6600000), (700100, 6600100)), srid=2154))

    def tearDown(self):
        del (self.trek)

    def test_save_with_same_geom(self):
        geom = LineString(((700000, 6600000), (700100, 6600100)), srid=2154)
        self.trek.geom = geom
        self.trek.save()
        retrieve_trek = Trek.objects.get(pk=self.trek.pk)
        self.assertTrue(retrieve_trek.geom.equals_exact(geom, tolerance=0.00001))

    def test_save_with_another_geom(self):
        geom = LineString(((-7, -7), (5, -7), (5, 5), (-7, 5), (-7, -7)), srid=2154)
        self.trek.geom = geom
        self.trek.save()
        retrieve_trek = Trek.objects.get(pk=self.trek.pk)
        self.assertFalse(retrieve_trek.geom.equals_exact(geom, tolerance=0.00001))

    def test_save_with_provided_one_field_exclusion(self):
        self.trek.save(update_fields=['geom'])
        self.assertTrue(self.trek.pk)

    def test_save_with_multiple_fields_exclusion(self):
        new_trek = TrekFactory.create()

        new_trek.description_en = 'Description Test update'
        new_trek.ambiance = 'Very special ambiance, for test purposes.'

        new_trek.save(update_fields=['description_en'])
        db_trek = Trek.objects.get(pk=new_trek.pk)

        self.assertTrue(db_trek.pk)
        self.assertEqual(db_trek.description_en, 'Description Test update')
        self.assertNotEqual(db_trek.ambiance, 'Very special ambiance, for test purposes.')

        new_trek.save(update_fields=['ambiance_en'])
        db_trek = Trek.objects.get(pk=new_trek.pk)

        self.assertEqual(db_trek.ambiance_en, 'Very special ambiance, for test purposes.')


class TrekItinerancyTest(TestCase):
    def test_next_previous(self):
        trekA = TrekFactory(name=u"A")
        trekB = TrekFactory(name=u"B")
        trekC = TrekFactory(name=u"C")
        trekD = TrekFactory(name=u"D")
        OrderedTrekChild(parent=trekC, child=trekA, order=42).save()
        OrderedTrekChild(parent=trekC, child=trekB, order=15).save()
        OrderedTrekChild(parent=trekD, child=trekA, order=1).save()
        self.assertEqual(trekA.children_id, [])
        self.assertEqual(trekB.children_id, [])
        self.assertEqual(trekC.children_id, [trekB.id, trekA.id])
        self.assertEqual(trekD.children_id, [trekA.id])
        self.assertEqual(trekA.next_id, {trekC.id: None, trekD.id: None})
        self.assertEqual(trekB.next_id, {trekC.id: trekA.id})
        self.assertEqual(trekC.next_id, {})
        self.assertEqual(trekD.next_id, {})
        self.assertEqual(trekA.previous_id, {trekC.id: trekB.id, trekD.id: None})
        self.assertEqual(trekB.previous_id, {trekC.id: None})
        self.assertEqual(trekC.previous_id, {})
        self.assertEqual(trekD.previous_id, {})

    def test_delete_child(self):
        trekA = TrekFactory(name=u"A")
        trekB = TrekFactory(name=u"B")
        trekC = TrekFactory(name=u"C")
        OrderedTrekChild(parent=trekA, child=trekB, order=1).save()
        OrderedTrekChild(parent=trekA, child=trekC, order=2).save()
        self.assertTrue(OrderedTrekChild.objects.filter(child=trekB).exists())
        self.assertQuerysetEqual(trekA.children, ['<Trek: B>', '<Trek: C>'])
        self.assertQuerysetEqual(trekB.parents, ['<Trek: A>'])
        self.assertQuerysetEqual(trekC.parents, ['<Trek: A>'])
        self.assertEqual(trekA.children_id, [trekB.id, trekC.id])
        self.assertEqual(trekB.parents_id, [trekA.id])
        self.assertEqual(trekC.parents_id, [trekA.id])
        trekB.delete()
        self.assertEqual(trekC.previous_id_for(trekA), None)
        self.assertEqual(trekC.next_id_for(trekA), None)
        self.assertEqual(trekC.next_id, {trekA.id: None})
        self.assertEqual(trekC.previous_id, {trekA.id: None})
        self.assertFalse(OrderedTrekChild.objects.filter(child=trekB).exists())
        self.assertQuerysetEqual(trekA.children, ['<Trek: C>'])
        self.assertQuerysetEqual(trekC.parents, ['<Trek: A>'])
        self.assertEqual(trekA.children_id, [trekC.id])
        self.assertEqual(trekC.parents_id, [trekA.id])

    def test_delete_parent(self):
        trekA = TrekFactory(name=u"A")
        trekB = TrekFactory(name=u"B")
        trekC = TrekFactory(name=u"C")
        OrderedTrekChild(parent=trekB, child=trekA, order=1).save()
        OrderedTrekChild(parent=trekC, child=trekA, order=2).save()
        self.assertTrue(OrderedTrekChild.objects.filter(parent=trekB).exists())
        self.assertQuerysetEqual(trekA.parents, ['<Trek: B>', '<Trek: C>'])
        self.assertQuerysetEqual(trekB.children, ['<Trek: A>'])
        self.assertQuerysetEqual(trekC.children, ['<Trek: A>'])
        self.assertEqual(trekA.parents_id, [trekB.id, trekC.id])
        self.assertEqual(trekB.children_id, [trekA.id])
        self.assertEqual(trekC.children_id, [trekA.id])
        trekB.delete()
        self.assertEqual(trekA.previous_id_for(trekC), None)
        self.assertEqual(trekA.next_id_for(trekC), None)
        self.assertEqual(trekA.next_id, {trekC.id: None})
        self.assertEqual(trekA.previous_id, {trekC.id: None})
        self.assertFalse(OrderedTrekChild.objects.filter(parent=trekB).exists())
        self.assertQuerysetEqual(trekA.parents, ['<Trek: C>'])
        self.assertQuerysetEqual(trekC.children, ['<Trek: A>'])
        self.assertEqual(trekA.parents_id, [trekC.id])
        self.assertEqual(trekC.children_id, [trekA.id])
