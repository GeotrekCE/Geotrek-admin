# -*- coding: utf-8 -*-
import math

from django.test import TestCase
from django.contrib.gis.geos import LineString
from django.db import IntegrityError

from geotrek.common.utils import dbnow
from geotrek.authent.factories import UserFactory
from geotrek.authent.models import Structure
from geotrek.core.factories import (PathFactory, StakeFactory)
from geotrek.core.models import Path


class StakeTest(TestCase):
    def test_comparison(self):
        low = StakeFactory.create()
        high = StakeFactory.create()
        # In case SERIAL field was reinitialized
        if high.pk < low.pk:
            tmp = high
            high = low
            low = tmp
            self.assertTrue(low.pk < high.pk)
        self.assertTrue(low < high)
        self.assertTrue(low <= high)
        self.assertFalse(low > high)
        self.assertFalse(low >= high)
        self.assertFalse(low == high)


class PathTest(TestCase):
    def test_paths_bystructure(self):
        user = UserFactory()
        p1 = PathFactory()
        p2 = PathFactory(structure=Structure.objects.create(name="other"))

        self.assertEqual(user.profile.structure, p1.structure)
        self.assertNotEqual(user.profile.structure, p2.structure)

        self.assertEqual(len(Structure.objects.all()), 2)
        self.assertEqual(len(Path.objects.all()), 2)

        self.assertEqual(Path.in_structure.for_user(user)[0], Path.for_user(user)[0])
        self.assertTrue(p1 in Path.in_structure.for_user(user))
        self.assertFalse(p2 in Path.in_structure.for_user(user))

        # Change user structure on-the-fly
        profile = user.profile
        profile.structure = p2.structure
        profile.save()

        self.assertEqual(user.profile.structure.name, "other")
        self.assertFalse(p1 in Path.in_structure.for_user(user))
        self.assertTrue(p2 in Path.in_structure.for_user(user))

    def test_dates(self):
        t1 = dbnow()
        p = PathFactory()
        t2 = dbnow()
        self.assertTrue(t1 < p.date_insert < t2,
                        msg='Date interval failed: %s < %s < %s' % (
                            t1, p.date_insert, t2
                        ))

        p.name = "Foo"
        p.save()
        t3 = dbnow()
        self.assertTrue(t2 < p.date_update < t3,
                        msg='Date interval failed: %s < %s < %s' % (t2, p.date_update, t3))

    def test_latestupdate_delete(self):
        for i in range(10):
            PathFactory.create()
        t1 = dbnow()
        self.assertTrue(t1 > Path.latest_updated())
        (Path.objects.all()[0]).delete()
        self.assertFalse(t1 > Path.latest_updated())

    def test_length(self):
        p1 = PathFactory.build()
        self.assertEqual(p1.length, 0)
        p2 = PathFactory.create()
        self.assertNotEqual(p2.length, 0)


class PathVisibilityTest(TestCase):
    def setUp(self):
        self.path = PathFactory()
        self.invisible = PathFactory(visible=False)

    def test_paths_are_visible_by_default(self):
        self.assertTrue(self.path.visible)

    def test_invisible_paths_do_not_appear_in_queryset(self):
        self.assertEqual(len(Path.objects.all()), 1)

    def test_latest_updated_bypass_invisible(self):
        self.assertEqual(Path.latest_updated(), self.path.date_update)

    def test_splitted_paths_do_not_become_visible(self):
        PathFactory(geom=LineString((10, 0), (12, 0)), visible=False)
        PathFactory(geom=LineString((11, 1), (11, -1)))
        self.assertEqual(len(Path.objects.all()), 3)


class PathGeometryTest(TestCase):
    def test_self_intersection_raises_integrity_error(self):
        # Create path with self-intersection
        def create_path():
            PathFactory.create(geom=LineString((0, 0), (2, 0), (1, 1), (1, -1)))
        self.assertRaises(IntegrityError, create_path)

    def test_valid_geometry_can_be_saved(self):
        PathFactory.create(geom=LineString((0, 0), (2, 0), (1, 1)))

    def test_modify_self_intersection_raises_integrity_error(self):
        p = PathFactory.create(geom=LineString((0, 0), (2, 0), (1, 1)))
        p.geom = LineString((0, 0), (2, 0), (1, 1), (1, -1))
        self.assertRaises(IntegrityError, p.save)

    def test_overlap_geometry(self):
        PathFactory.create(geom=LineString((0, 0), (60, 0)))
        p = PathFactory.create(geom=LineString((40, 0), (50, 0)))
        self.assertTrue(p.is_overlap())
        # Overlaping twice
        p = PathFactory.create(geom=LineString((20, 1), (20, 0), (25, 0), (25, 1),
                                               (30, 1), (30, 0), (35, 0), (35, 1)))
        self.assertTrue(p.is_overlap())

        # But crossing is ok
        p = PathFactory.create(geom=LineString((6, 1), (6, 3)))
        self.assertFalse(p.is_overlap())
        # Touching is ok too
        p = PathFactory.create(geom=LineString((5, 1), (5, 0)))
        self.assertFalse(p.is_overlap())
        # Touching twice is ok too
        p = PathFactory.create(geom=LineString((2.5, 0), (3, 1), (3.5, 0)))
        self.assertFalse(p.is_overlap())

    def test_snapping(self):
        # Sinosoid line
        coords = [(x, math.sin(x)) for x in range(10)]
        PathFactory.create(geom=LineString(*coords))
        """
               +
          /--\ |
         /    \|
        +      +      +
                \    /
                 \--/
        """
        # Snap end
        path_snapped = PathFactory.create(geom=LineString((10, 10), (5, -1)))  # math.sin(5) == -0.96..
        self.assertEqual(len(Path.objects.all()), 3)
        self.assertEqual(path_snapped.geom.coords, ((10, 10), coords[5]))

        # Snap start
        path_snapped = PathFactory.create(geom=LineString((3, 0), (5, -5)))  # math.sin(3) == 0.14..
        self.assertEqual(path_snapped.geom.coords, (coords[3], (5, -5)))

        # Snap both
        path_snapped = PathFactory.create(geom=LineString((0, 0), (3.0, 0)))
        self.assertEqual(path_snapped.geom.coords, ((0, 0), (3.0, math.sin(3))))

    def test_snapping_choose_closest_point(self):
        # Line with several points in less than PATH_SNAPPING_DISTANCE
        PathFactory.create(geom=LineString((0, 0), (9.8, 0), (9.9, 0), (10, 0)))
        path_snapped = PathFactory.create(geom=LineString((10, 0.1), (10, 10)))
        self.assertEqual(path_snapped.geom.coords, ((10, 0), (10, 10)))

    def test_snapping_is_idempotent(self):
        PathFactory.create(geom=LineString((0, 0), (9.8, 0), (9.9, 0), (10, 0)))
        path_snapped = PathFactory.create(geom=LineString((10, 0.1), (10, 10)))
        old_geom = path_snapped.geom
        path_snapped.geom = old_geom
        path_snapped.save()
        self.assertEqual(path_snapped.geom.coords, old_geom.coords)
