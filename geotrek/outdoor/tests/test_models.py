import json

from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos.collections import GeometryCollection
from django.contrib.gis.geos.point import GEOSGeometry, Point
from django.test import TestCase, override_settings
from mapentity.middleware import clear_internal_user_cache

from geotrek.common.tests.factories import OrganismFactory
from geotrek.outdoor.models import (ChildCoursesExistError, ChildSitesExistError, CourseType, Rating, RatingScale, Site,
                                    SiteType)
from geotrek.outdoor.tests.factories import (CourseFactory, CourseTypeFactory,
                                             PracticeFactory, RatingFactory,
                                             RatingScaleFactory, SectorFactory,
                                             SiteFactory, SiteTypeFactory)
from geotrek.trekking.tests.factories import POIFactory


class SiteTest(TestCase):
    @override_settings(PUBLISHED_BY_LANG=False)
    def test_published_children(self):
        parent = SiteFactory(name='parent')
        SiteFactory(name='child1', parent=parent, published=False)
        child_2 = SiteFactory(name='child2', parent=parent, published=True)
        self.assertListEqual(list(parent.published_children.values_list('pk', flat=True)), [child_2.pk])

    def test_published_children_by_lang(self):
        parent = SiteFactory(name='parent')
        SiteFactory(name='child1', parent=parent, published=False)
        child_2 = SiteFactory(name='child2', parent=parent, published_en=True)
        child_3 = SiteFactory(name='child3', parent=parent, published_fr=True)
        self.assertListEqual(list(parent.published_children.values_list('pk', flat=True)),
                             [child_2.pk, child_3.pk])

    def test_validate_collection_geometrycollection(self):
        site_simple = SiteFactory.create(name='site',
                                         geom='GEOMETRYCOLLECTION(POINT(0 0), POLYGON((1 1, 2 2, 1 2, 1 1))))')
        self.assertEqual(site_simple.geom.wkt,
                         GEOSGeometry('GEOMETRYCOLLECTION(POINT(0 0), POLYGON((1 1, 2 2, 1 2, 1 1)))').wkt
                         )
        site_complex_geom = SiteFactory.create(name='site',
                                               geom='GEOMETRYCOLLECTION(MULTIPOINT(0 0, 1 1), '
                                                    'POLYGON((1 1, 2 2, 1 2, 1 1))))')
        self.assertEqual(site_complex_geom.geom.wkt,
                         GEOSGeometry('GEOMETRYCOLLECTION(POINT(0 0), POINT(1 1), POLYGON((1 1, 2 2, 1 2, 1 1)))').wkt
                         )
        site_multiple_point = SiteFactory.create(name='site',
                                                 geom='GEOMETRYCOLLECTION(POINT(0 0), POINT(1 1), POINT(1 2))')
        self.assertEqual(site_multiple_point.geom.wkt,
                         GEOSGeometry('GEOMETRYCOLLECTION(POINT(0 0), POINT(1 1), POINT(1 2)))').wkt
                         )
        site_multiple_geomcollection = SiteFactory.create(name='site',
                                                          geom='GEOMETRYCOLLECTION('
                                                               'GEOMETRYCOLLECTION(POINT(0 0)),'
                                                               'GEOMETRYCOLLECTION(POINT(1 1)), '
                                                               'GEOMETRYCOLLECTION(POINT(1 2)))')
        self.assertEqual(site_multiple_geomcollection.geom.wkt,
                         'GEOMETRYCOLLECTION (POINT (0 0), POINT (1 1), POINT (1 2))')

    def test_delete_method_delete_site_with_child_sites_and_courses(self):
        self.parent_site = SiteFactory.create(name="parent_site")
        self.child_site = SiteFactory.create(name="child_site", parent=self.parent_site)

        self.parent_site_of_course = SiteFactory.create(name="parent_site_of_course")
        self.child_course = CourseFactory.create(name="child_course", parent_sites=[self.parent_site_of_course])

        # We can't delete a parent if it has children
        with self.assertRaises(ChildSitesExistError):
            self.parent_site.delete()
        self.assertEqual(Site.objects.filter(pk=self.parent_site.pk).exists(), True)

        with self.assertRaises(ChildCoursesExistError):
            self.parent_site_of_course.delete()
        self.assertEqual(Site.objects.filter(pk=self.parent_site_of_course.pk).exists(), True)

        # But we can delete the children
        self.child_site.delete()
        self.child_course.delete()

    def test_duplicate_site_doesnt_duplicate_children(self):
        self.site_1 = SiteFactory.create(name="parent_site")
        self.site_2 = SiteFactory.create(name="child_site", parent=self.site_1)
        self.assertEqual(Site.objects.count(), 2)
        self.site_1.duplicate()
        # Means that only the parent_site is duplicated and not his child
        self.assertEqual(Site.objects.count(), 3)


class SiteSuperTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        org_a = OrganismFactory(organism='a')
        org_b = OrganismFactory(organism='b')
        org_c = OrganismFactory(organism='c')
        cls.alone = SiteFactory(
            practice=None
        )
        cls.parent = SiteFactory(
            practice__name='Bbb',
            practice__sector__name='Bxx',
            managers=[org_a, org_b],
            orientation=['N', 'S'],
            wind=['N', 'S']
        )
        cls.child = SiteFactory(
            parent=cls.parent,
            practice__name='Aaa',
            practice__sector__name='Axx',
            managers=[org_b, org_c],
            orientation=['E', 'S'],
            wind=['E', 'S']
        )
        cls.grandchild1 = SiteFactory(
            parent=cls.child,
            practice=cls.parent.practice,
            orientation=cls.parent.orientation,
            wind=cls.parent.wind
        )
        cls.grandchild2 = SiteFactory(
            parent=cls.child,
            practice=None,
            orientation=[],
            wind=[]
        )

    def test_super_practices_descendants(self):
        self.assertListEqual(list(self.parent.super_practices.values_list('name', flat=True)),
                             ['Aaa', 'Bbb'])

    def test_super_practices_ascendants(self):
        self.assertListEqual(list(self.grandchild2.super_practices.values_list('pk', flat=True)),
                             [])

    def test_super_sectors_descendants(self):
        self.assertListEqual(list(self.parent.super_sectors.values_list('name', flat=True)),
                             ['Axx', 'Bxx'])

    def test_super_sectors_ascendants(self):
        self.assertListEqual(list(self.grandchild2.super_sectors.values_list('name', flat=True)),
                             [])

    def test_super_orientation_descendants(self):
        self.assertListEqual(self.parent.super_orientation, ['N', 'E', 'S'])

    def test_super_orientation_ascendants(self):
        self.assertListEqual(self.grandchild2.super_orientation, [])

    def test_super_wind_descendants(self):
        self.assertEqual(self.parent.super_wind, ['N', 'E', 'S'])

    def test_super_wind_ascendants(self):
        self.assertEqual(self.grandchild2.super_wind, [])

    def test_super_managers_descendants(self):
        self.assertListEqual(list(self.parent.super_managers.values_list('organism', flat=True)),
                             ['a', 'b', 'b', 'c'])

    def test_super_managers_ascendants(self):
        self.assertListEqual(list(self.grandchild2.super_managers.values_list('pk', flat=True)), [])

    def test_super_practices_display(self):
        self.assertEqual(self.alone.super_practices_display, "")
        self.assertEqual(self.parent.super_practices_display, "<i>Aaa</i>, Bbb")
        self.assertEqual(self.child.super_practices_display, "Aaa, <i>Bbb</i>")
        self.assertEqual(self.grandchild1.super_practices_display, "Bbb")
        self.assertEqual(self.grandchild2.super_practices_display, "")


class SectorTest(TestCase):
    def test_sector_str(self):
        sector = SectorFactory.create(name='Baz')
        self.assertEqual(str(sector), 'Baz')

    def test_cascading_deletion(self):
        practice = PracticeFactory()
        rating_scale = RatingScaleFactory(practice=practice)
        rating = RatingFactory(scale=rating_scale)
        site_type = SiteTypeFactory(practice=practice)
        course_type = CourseTypeFactory(practice=practice)
        clear_internal_user_cache()
        practice_pk = practice.pk
        practice_repr = str(practice)
        rating_scale_pk = rating_scale.pk
        rating_scale_repr = str(rating_scale)
        rating_pk = rating.pk
        site_type_pk = site_type.pk
        course_type_pk = course_type.pk
        practice.delete()
        model_num = ContentType.objects.get_for_model(RatingScale).pk
        entry = LogEntry.objects.get(content_type=model_num, object_id=rating_scale_pk)
        self.assertEqual(entry.change_message, f"Deleted by cascade from Practice {practice_pk} - {practice_repr}")
        self.assertEqual(entry.action_flag, DELETION)
        model_num = ContentType.objects.get_for_model(Rating).pk
        entry = LogEntry.objects.get(content_type=model_num, object_id=rating_pk)
        self.assertEqual(entry.change_message, f"Deleted by cascade from RatingScale {rating_scale_pk} - {rating_scale_repr}")
        self.assertEqual(entry.action_flag, DELETION)
        model_num = ContentType.objects.get_for_model(CourseType).pk
        entry = LogEntry.objects.get(content_type=model_num, object_id=course_type_pk)
        self.assertEqual(entry.change_message, f"Deleted by cascade from Practice {practice_pk} - {practice_repr}")
        self.assertEqual(entry.action_flag, DELETION)
        model_num = ContentType.objects.get_for_model(SiteType).pk
        entry = LogEntry.objects.get(content_type=model_num, object_id=site_type_pk)
        self.assertEqual(entry.change_message, f"Deleted by cascade from Practice {practice_pk} - {practice_repr}")
        self.assertEqual(entry.action_flag, DELETION)


class RatingScaleTest(TestCase):
    def test_ratingscale_str(self):
        scale = RatingScaleFactory.create(name='Bar', practice__name='Foo')
        self.assertEqual(str(scale), 'Bar (Foo)')


class ExcludedPOIsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.poi1 = POIFactory()
        cls.poi1.geom = Point(0.5, 0.5, srid=2154)
        cls.poi1.save()
        cls.poi2 = POIFactory()
        cls.poi2.geom = Point(0.5, 0.5, srid=2154)
        cls.poi2.save()
        cls.site = SiteFactory(geom=GeometryCollection(Polygon(((0, 0), (0, 1), (1, 0), (1, 1), (0, 0)), srid=2154)))

    def test_no_poi_excluded(self):
        self.assertEqual(self.site.pois.count(), 2)

    def test_one_poi_excluded(self):
        self.site.pois_excluded.set([self.poi1])
        self.assertEqual(self.site.pois.count(), 1)


class CourseTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.course_without_points_reference = CourseFactory()
        cls.course_with_points_reference = CourseFactory(points_reference='SRID=2154;MULTIPOINT((575631.94 6373472.27), (576015.10 6372811.10))')

    def test_points_reference_geojson_null(self):
        """ Course points_reference geojson property should be None if null in database """
        geojson = self.course_without_points_reference.points_reference_geojson
        self.assertIsNone(geojson)

    def test_points_reference_geojson_not_null(self):
        """ Course points_reference geojson property should be reprojected in geojson format if defined in database """
        geojson_text = self.course_with_points_reference.points_reference_geojson
        geojson = json.loads(geojson_text)
        coordinates = geojson['coordinates']
        self.assertAlmostEqual(coordinates[0][0], 1.43697743457888)
        self.assertAlmostEqual(coordinates[0][1], 44.449222490604605)
        self.assertAlmostEqual(coordinates[1][0], 1.441955564370652)
        self.assertAlmostEqual(coordinates[1][1], 44.443339997352474)
