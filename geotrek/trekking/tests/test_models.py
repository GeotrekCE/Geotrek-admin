import datetime
import os
from unittest import skipIf

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import (LineString, MultiLineString, MultiPoint,
                                     MultiPolygon, Point, Polygon)
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test.utils import override_settings
from easy_thumbnails.files import ThumbnailFile

from geotrek.common.tests.factories import LabelFactory, AttachmentImageFactory, AttachmentPictoSVGFactory

from geotrek.common.tests import TranslationResetMixin
from geotrek.core.tests.factories import PathFactory
from geotrek.trekking.models import (OrderedTrekChild, Rating, RatingScale,
                                     Trek)
from geotrek.trekking.tests.factories import (POIFactory, PracticeFactory,
                                              RatingFactory,
                                              RatingScaleFactory,
                                              ServiceFactory, TrekFactory,
                                              TrekWithPOIsFactory,
                                              WebLinkCategoryFactory,
                                              WebLinkFactory)
from geotrek.zoning.tests.factories import CityFactory, DistrictFactory


class TrekTest(TranslationResetMixin, TestCase):
    def test_is_public_if_parent_published(self):
        t = TrekFactory.create(published=False)
        parent = TrekFactory.create(published=True)
        OrderedTrekChild.objects.create(parent=parent, child=t)
        self.assertTrue(t.is_public())

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

    @override_settings(PUBLISHED_BY_LANG=False)
    def test_any_published_without_published_by_lang(self):
        t = TrekFactory.create(published=False)
        t.published_fr = True
        t.save()
        self.assertFalse(t.any_published)

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

    @override_settings(PUBLISHED_BY_LANG=False)
    def test_published_status_without_published_by_lang(self):
        t = TrekFactory.create(published=True)
        t.published_fr = False
        t.published_it = False
        t.save()
        self.assertEqual(t.published_status, [
            {'lang': 'en', 'language': 'English', 'status': True},
            {'lang': 'es', 'language': 'Spanish', 'status': True},
            {'lang': 'fr', 'language': 'French', 'status': True},
            {'lang': 'it', 'language': 'Italian', 'status': True}])

    @override_settings(PUBLISHED_BY_LANG=False)
    def test_published_langs_without_published_by_lang_not_published(self):
        t = TrekFactory.create(published=False)
        t.published_fr = True
        t.published_it = True
        t.save()
        self.assertEqual(t.published_langs, [])

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_kml_coordinates_should_be_3d(self):
        trek = TrekWithPOIsFactory.create()
        kml = trek.kml()
        parsed = BeautifulSoup(kml, features='xml')
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

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_delete_cascade(self):
        p1 = PathFactory.create()
        p2 = PathFactory.create()
        t = TrekFactory.create(paths=[p1, p2])

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
        self.assertListEqual(list(Trek.objects.all().values_list('name', flat=True)),
                             ['A', 'B', 'Ca', 'Cb'])

    def test_trek_itself_as_parent(self):
        """
        Test if a trek it is its own parent
        """
        trek1 = TrekFactory.create(name='trek1')
        OrderedTrekChild.objects.create(parent=trek1, child=trek1)
        self.assertRaisesMessage(ValidationError,
                                 "Cannot use itself as child trek.",
                                 trek1.full_clean)

    def test_pictures_print_thumbnail_correct_picture(self):
        trek = TrekFactory()
        AttachmentImageFactory.create_batch(5, content_object=trek)
        self.assertEqual(trek.pictures.count(), 5)
        self.assertEqual(len(os.listdir(os.path.dirname(trek.attachments.first().attachment_file.path))), 5, os.listdir(os.path.dirname(trek.attachments.first().attachment_file.path)))
        self.assertTrue(isinstance(trek.picture_print, ThumbnailFile))

    def test_pictures_print_thumbnail_wrong_picture(self):
        trek = TrekFactory()
        error_image_attachment = AttachmentPictoSVGFactory(content_object=trek)
        os.unlink(error_image_attachment.attachment_file.path)
        self.assertIsNone(trek.picture_print)

    def test_pictures_print_thumbnail_no_picture(self):
        trek = TrekFactory()
        self.assertEqual(trek.pictures.count(), 0)
        self.assertIsNone(trek.picture_print, ThumbnailFile)

    def test_thumbnail(self):
        trek = TrekFactory()
        AttachmentImageFactory(content_object=trek)
        self.assertTrue(isinstance(trek.thumbnail, ThumbnailFile))
        self.assertIsNotNone(trek.thumbnail)
        self.assertIn(trek.thumbnail.name, trek.thumbnail_display)


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
        self.test_takes_current_date_when_published_becomes_true()
        old_date = datetime.date(2003, 8, 6)
        self.trek.publication_date = old_date
        self.trek.save()
        self.assertEqual(self.trek.publication_date, old_date)


class RelatedObjectsTest(TranslationResetMixin, TestCase):
    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_helpers(self):

        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        p2 = PathFactory.create(geom=LineString((4, 4), (8, 8)))
        trek = TrekFactory.create(paths=[(p1, 0.5, 1), (p2, 0, 1)])
        poi = POIFactory.create(paths=[(p1, 0.6, 0.6)])
        poi2 = POIFactory.create(paths=[(p1, 0.6, 0.6)])
        service = ServiceFactory.create(paths=[(p1, 0.7, 0.7)])
        service.type.practices.add(trek.practice)
        trek.pois_excluded.add(poi2.pk)

        # /!\ District are automatically linked to paths at DB level
        d1 = DistrictFactory.create(geom=MultiPolygon(
            Polygon(((-2, -2), (3, -2), (3, 3), (-2, 3), (-2, -2)))))
        # Ensure related objects are accessible
        self.assertCountEqual(trek.pois_excluded.all(), [poi2])
        self.assertCountEqual(trek.all_pois, [poi, poi2])
        self.assertCountEqual(trek.pois, [poi])
        self.assertCountEqual(trek.services, [service])
        self.assertCountEqual(poi.treks, [trek])
        self.assertCountEqual(service.treks, [trek])
        self.assertCountEqual(trek.districts, [d1])

        # Ensure there is no duplicates

        self.assertCountEqual(trek.pois_excluded.all(), [poi2])
        self.assertCountEqual(trek.all_pois, [poi, poi2])
        self.assertCountEqual(trek.pois, [poi])
        self.assertCountEqual(trek.services, [service])
        self.assertCountEqual(poi.treks, [trek])
        self.assertCountEqual(service.treks, [trek])

        d2 = DistrictFactory.create(geom=MultiPolygon(
            Polygon(((3, 3), (9, 3), (9, 9), (3, 9), (3, 3)))))
        self.assertCountEqual(trek.districts, [d1, d2])

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_helpers_nds(self):
        trek = TrekFactory.create(geom=LineString((2, 2), (8, 8)))
        poi = POIFactory.create(geom=Point(2.4, 2.4))
        poi2 = POIFactory.create(geom=Point(2.4, 2.4))
        service = ServiceFactory.create(geom=Point(2.8, 2.8))
        service.type.practices.add(trek.practice)
        trek.pois_excluded.add(poi2.pk)

        # /!\ District are automatically linked to paths at DB level
        d1 = DistrictFactory.create(geom=MultiPolygon(
            Polygon(((-2, -2), (3, -2), (3, 3), (-2, 3), (-2, -2)))))
        # Ensure related objects are accessible
        self.assertCountEqual(trek.pois_excluded.all(), [poi2])
        self.assertCountEqual(trek.all_pois, [poi, poi2])
        self.assertCountEqual(trek.pois, [poi])
        self.assertCountEqual(trek.services, [service])
        self.assertCountEqual(poi.treks, [trek])
        self.assertCountEqual(service.treks, [trek])
        self.assertCountEqual(trek.districts, [d1])

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_deleted_pois_nds(self):
        trek = TrekFactory.create(geom=LineString((0, 0), (4, 4)))
        poi = POIFactory.create(geom=Point(2.4, 2.4))
        self.assertCountEqual(trek.pois, [poi])
        poi.delete()
        self.assertCountEqual(trek.pois, [])

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_deleted_services_nds(self):
        trek = TrekFactory.create(geom=LineString((0, 0), (4, 4)))
        service = ServiceFactory.create(geom=Point(2.4, 2.4))
        service.type.practices.add(trek.practice)
        self.assertCountEqual(trek.services, [service])
        service.delete()
        self.assertCountEqual(trek.services, [])

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_deleted_pois(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        trek = TrekFactory.create(paths=[p1])
        poi = POIFactory.create(paths=[(p1, 0.6, 0.6)])
        self.assertCountEqual(trek.pois, [poi])
        poi.delete()
        self.assertCountEqual(trek.pois, [])

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_deleted_services(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        trek = TrekFactory.create(paths=[p1])
        service = ServiceFactory.create(paths=[(p1, 0.6, 0.6)])
        service.type.practices.add(trek.practice)
        self.assertCountEqual(trek.services, [service])
        service.delete()
        self.assertCountEqual(trek.services, [])

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_pois_should_be_ordered_by_progression(self):
        p1 = PathFactory.create(geom=LineString((0, 0), (4, 4)))
        p2 = PathFactory.create(geom=LineString((4, 4), (8, 8)))
        self.trek = TrekFactory.create(paths=[p1, p2])

        self.trek_reverse = TrekFactory.create(paths=[(p2, 0.8, 0), (p1, 1, 0.2)])

        self.poi1 = POIFactory.create(paths=[(p1, 0.8, 0.8)])
        self.poi2 = POIFactory.create(paths=[(p1, 0.3, 0.3)])
        self.poi3 = POIFactory.create(paths=[(p2, 0.5, 0.5)])

        pois = self.trek.pois
        self.assertEqual([self.poi2, self.poi1, self.poi3], list(pois))
        pois = self.trek_reverse.pois
        self.assertEqual([self.poi3, self.poi1, self.poi2], list(pois))

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_pois_is_not_ordered_by_progression(self):
        self.trek = TrekFactory.create(geom=LineString((0, 0), (8, 8)))

        self.trek_reverse = TrekFactory.create(geom=LineString((6.4, 6.4), (0.8, 0.8)))

        self.poi1 = POIFactory.create(geom=Point(3.2, 3.2))
        self.poi2 = POIFactory.create(geom=Point(1.2, 1.2))
        self.poi3 = POIFactory.create(geom=Point(4, 4))

        pois = self.trek.pois
        self.assertCountEqual([self.poi1, self.poi2, self.poi3], pois)
        pois = self.trek_reverse.pois
        self.assertCountEqual([self.poi1, self.poi2, self.poi3], pois)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_city_departure(self):

        p1 = PathFactory.create(geom=LineString((0, 0), (5, 5)))
        trek = TrekFactory.create(paths=[p1])
        self.assertEqual(trek.city_departure, '')

        city1 = CityFactory.create(geom=MultiPolygon(Polygon(((-1, -1), (3, -1), (3, 3),
                                                              (-1, 3), (-1, -1)))))
        city2 = CityFactory.create(geom=MultiPolygon(Polygon(((3, 3), (9, 3), (9, 9),
                                                              (3, 9), (3, 3)))))
        self.assertEqual([city for city in trek.cities], [city1, city2])
        self.assertEqual(trek.city_departure, str(city1))

    @skipIf(settings.TREKKING_TOPOLOGY_ENABLED, 'Test without dynamic segmentation only')
    def test_city_departure_nds(self):
        trek = TrekFactory.create(geom=LineString((0, 0), (5, 5)))
        self.assertEqual(trek.city_departure, '')

        city1 = CityFactory.create(geom=MultiPolygon(Polygon(((-1, -1), (3, -1), (3, 3),
                                                              (-1, 3), (-1, -1)))))
        city2 = CityFactory.create(geom=MultiPolygon(Polygon(((3, 3), (9, 3), (9, 9),
                                                              (3, 9), (3, 3)))))
        self.assertEqual([city for city in trek.cities], [city1, city2])
        self.assertEqual(trek.city_departure, str(city1))


class TrekUpdateGeomTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trek = TrekFactory.create(published=True, geom=LineString(((700000, 6600000), (700100, 6600100)), srid=2154))

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
        if settings.TREKKING_TOPOLOGY_ENABLED:
            self.assertFalse(retrieve_trek.geom.equals_exact(geom, tolerance=0.00001))
        else:
            self.assertTrue(retrieve_trek.geom.equals_exact(geom, tolerance=0.00001))

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
        trekA = TrekFactory(name="A")
        trekB = TrekFactory(name="B")
        trekC = TrekFactory(name="C")
        trekD = TrekFactory(name="D")
        OrderedTrekChild(parent=trekC, child=trekA, order=42).save()
        OrderedTrekChild(parent=trekC, child=trekB, order=15).save()
        OrderedTrekChild(parent=trekD, child=trekA, order=1).save()
        self.assertEqual(list(trekA.children_id), [])
        self.assertEqual(list(trekB.children_id), [])
        self.assertEqual(list(trekC.children_id), [trekB.id, trekA.id])
        self.assertEqual(list(trekD.children_id), [trekA.id])
        self.assertEqual(trekA.next_id, {trekC.id: None, trekD.id: None})
        self.assertEqual(trekB.next_id, {trekC.id: trekA.id})
        self.assertEqual(trekC.next_id, {})
        self.assertEqual(trekD.next_id, {})
        self.assertEqual(trekA.previous_id, {trekC.id: trekB.id, trekD.id: None})
        self.assertEqual(trekB.previous_id, {trekC.id: None})
        self.assertEqual(trekC.previous_id, {})
        self.assertEqual(trekD.previous_id, {})

    def test_delete_child(self):
        trekA = TrekFactory(name="A")
        trekB = TrekFactory(name="B")
        trekC = TrekFactory(name="C")
        OrderedTrekChild(parent=trekA, child=trekB, order=1).save()
        OrderedTrekChild(parent=trekA, child=trekC, order=2).save()
        self.assertTrue(OrderedTrekChild.objects.filter(child=trekB).exists())
        self.assertListEqual(list(trekA.children.values_list('name', flat=True)), ['B', 'C'])
        self.assertListEqual(list(trekB.parents.values_list('name', flat=True)), ['A'])
        self.assertListEqual(list(trekC.parents.values_list('name', flat=True)), ['A'])
        self.assertEqual(list(trekA.children_id), [trekB.id, trekC.id])
        self.assertEqual(trekB.parents_id, [trekA.id])
        self.assertEqual(trekC.parents_id, [trekA.id])
        trekB.delete()
        self.assertEqual(trekC.previous_id_for(trekA), None)
        self.assertEqual(trekC.next_id_for(trekA), None)
        self.assertEqual(trekC.next_id, {trekA.id: None})
        self.assertEqual(trekC.previous_id, {trekA.id: None})
        self.assertFalse(OrderedTrekChild.objects.filter(child=trekB).exists())
        self.assertListEqual(list(trekA.children.values_list('name', flat=True)), ['C'])
        self.assertListEqual(list(trekC.parents.values_list('name', flat=True)), ['A'])
        self.assertEqual(list(trekA.children_id), [trekC.id])
        self.assertEqual(trekC.parents_id, [trekA.id])

    def test_delete_parent(self):
        trekA = TrekFactory(name="A")
        trekB = TrekFactory(name="B")
        trekC = TrekFactory(name="C")
        OrderedTrekChild(parent=trekB, child=trekA, order=1).save()
        OrderedTrekChild(parent=trekC, child=trekA, order=2).save()
        self.assertTrue(OrderedTrekChild.objects.filter(parent=trekB).exists())
        self.assertListEqual(list(trekA.parents.values_list('name', flat=True)), ['B', 'C'])
        self.assertListEqual(list(trekB.children.values_list('name', flat=True)), ['A'])
        self.assertListEqual(list(trekC.children.values_list('name', flat=True)), ['A'])
        self.assertEqual(trekA.parents_id, [trekB.id, trekC.id])
        self.assertEqual(list(trekB.children_id), [trekA.id])
        self.assertEqual(list(trekC.children_id), [trekA.id])
        trekB.delete()
        self.assertEqual(trekA.previous_id_for(trekC), None)
        self.assertEqual(trekA.next_id_for(trekC), None)
        self.assertEqual(trekA.next_id, {trekC.id: None})
        self.assertEqual(trekA.previous_id, {trekC.id: None})
        self.assertFalse(OrderedTrekChild.objects.filter(parent=trekB).exists())
        self.assertListEqual(list(trekA.parents.values_list('name', flat=True)), ['C'])
        self.assertListEqual(list(trekC.children.values_list('name', flat=True)), ['A'])
        self.assertEqual(trekA.parents_id, [trekC.id])
        self.assertEqual(list(trekC.children_id), [trekA.id])


class MapImageExtentTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.trek = TrekFactory.create(
            points_reference=MultiPoint([Point(0, 0), Point(1, 1)], srid=settings.SRID),
            parking_location=Point(0, 0, srid=settings.SRID),
        )
        POIFactory.create(paths=[(cls.trek.paths.first(), 0.25, 0.25)], published=True)

    def test_get_map_image_extent(self):
        lng_min, lat_min, lng_max, lat_max = self.trek.get_map_image_extent()
        self.assertAlmostEqual(lng_min, -1.3630812101179004)
        self.assertAlmostEqual(lat_min, -5.983856309208769)
        self.assertAlmostEqual(lng_max, 3.001303976720215)
        self.assertAlmostEqual(lat_max, 46.50090044234927)


class RatingScaleTest(TestCase):
    def test_ratingscale_str(self):
        scale = RatingScaleFactory.create(name='Bar', practice__name='Foo')
        self.assertEqual(str(scale), 'Bar (Foo)')


class RatingTest(TestCase):
    def test_rating_str(self):
        scale = RatingFactory.create(name='Bar')
        self.assertEqual(str(scale), 'RatingScale : Bar')


class CascadedDeletionLoggingTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.practice = PracticeFactory(name="Pratice A")
        cls.scale = RatingScaleFactory(practice=cls.practice, name="Scale A")
        cls.rating = RatingFactory(scale=cls.scale)
        cls.categ = WebLinkCategoryFactory()
        cls.weblink = WebLinkFactory(category=cls.categ)

    def test_cascading_from_practice(self):
        practice_pk = self.practice.pk
        self.practice.delete()
        rating_model_num = ContentType.objects.get_for_model(Rating).pk
        scale_model_num = ContentType.objects.get_for_model(RatingScale).pk
        scale_entry = LogEntry.objects.get(content_type=scale_model_num, object_id=self.scale.pk)
        rating_entry = LogEntry.objects.get(content_type=rating_model_num, object_id=self.rating.pk)
        self.assertEqual(scale_entry.change_message, f"Deleted by cascade from Practice {practice_pk} - Pratice A")
        self.assertEqual(scale_entry.action_flag, DELETION)
        self.assertEqual(rating_entry.change_message, f"Deleted by cascade from RatingScale {self.scale.pk} - Scale A (Pratice A)")
        self.assertEqual(rating_entry.action_flag, DELETION)


class TrekLabelsTestCase(TestCase):
    def setUp(self):
        self.trek = TrekFactory()
        self.published_label = LabelFactory(published=True)
        self.unpublished_label = LabelFactory(published=False)

        self.trek.labels.set([self.published_label, self.unpublished_label])

    def test_published_label_property(self):
        self.assertEqual(self.trek.published_labels, [self.published_label])
