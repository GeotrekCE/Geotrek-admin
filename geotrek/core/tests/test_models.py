import math
import os
from unittest import mock, skipIf

from django.apps import apps
from django.conf import settings
from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import LineString, Point
from django.core import mail
from django.db import DEFAULT_DB_ALIAS, IntegrityError, connections
from django.db.models import ProtectedError
from django.template.loader import get_template
from django.test import TestCase
from django.test.utils import override_settings
from mapentity.middleware import clear_internal_user_cache

from geotrek.authent.models import Structure
from geotrek.authent.tests.factories import StructureFactory, UserFactory
from geotrek.common.utils import dbnow
from geotrek.core.models import (CertificationTrail, Path, PathAggregation,
                                 Trail)
from geotrek.core.tests.factories import (CertificationLabelFactory,
                                          CertificationStatusFactory,
                                          CertificationTrailFactory,
                                          ComfortFactory, PathFactory,
                                          StakeFactory, TrailCategoryFactory,
                                          TrailFactory)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
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


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PathTest(TestCase):
    def test_paths_bystructure(self):
        user = UserFactory()
        p1 = PathFactory()
        p2 = PathFactory(structure=Structure.objects.create(name="other"))

        self.assertEqual(user.profile.structure, p1.structure)
        self.assertNotEqual(user.profile.structure, p2.structure)

        self.assertEqual(len(Structure.objects.all()), 2)
        self.assertEqual(len(Path.objects.all()), 2)

        self.assertTrue(p1 in Path.objects.filter(structure=user.profile.structure))
        self.assertFalse(p2 in Path.objects.filter(structure=user.profile.structure))

        # Change user structure on-the-fly
        profile = user.profile
        profile.structure = p2.structure
        profile.save()

        self.assertEqual(user.profile.structure.name, "other")
        self.assertFalse(p1 in Path.objects.filter(structure=user.profile.structure))
        self.assertTrue(p2 in Path.objects.filter(structure=user.profile.structure))

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

    def test_extent(self):
        p1 = PathFactory.create()
        lng_min, lat_min, lng_max, lat_max = p1.extent
        self.assertAlmostEqual(lng_min, 3.0)
        self.assertAlmostEqual(lat_min, 46.499999999999936)
        self.assertAlmostEqual(lng_max, 3.0013039767202154)
        self.assertAlmostEqual(lat_max, 46.50090044234927)

    @override_settings(ALERT_DRAFT=True)
    def test_status_draft_alert(self):
        p1 = PathFactory.create()
        p1.save()
        self.assertEqual(len(mail.outbox), 0)
        p1.draft = True
        p1.save()
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(ALERT_DRAFT=True)
    @mock.patch('geotrek.core.models.mail_managers')
    def test_status_draft_fail_mail(self, mock_mail):
        mock_mail.side_effect = Exception("Test")
        p1 = PathFactory.create()
        p1.save()
        self.assertEqual(len(mail.outbox), 0)
        p1.draft = True
        p1.save()
        self.assertEqual(len(mail.outbox), 0)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_delete_allow_path_trigger(self):
        p1 = PathFactory.create()
        p2 = PathFactory.create()
        TrailFactory.create(paths=[p1])
        conn = connections[DEFAULT_DB_ALIAS]
        cur = conn.cursor()
        cur.execute(f"DELETE FROM core_path WHERE id = {p1.pk}")
        cur.execute(f"DELETE FROM core_path WHERE id = {p2.pk}")
        self.assertEqual(Path.objects.count(), 0)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    @override_settings(ALLOW_PATH_DELETION_TOPOLOGY=False)
    def test_delete_protected_allow_path_trigger(self):
        p1 = PathFactory.create()
        p2 = PathFactory.create()
        TrailFactory.create(paths=[p1])

        conn = connections[DEFAULT_DB_ALIAS]
        cur = conn.cursor()

        app = apps.get_app_config('core')
        sql_file = os.path.normpath(os.path.join(app.path, 'templates', app.label, 'sql', 'post_80_paths_deletion.sql'))
        template = get_template(sql_file)
        context_settings = settings.__dict__['_wrapped'].__dict__
        context = dict(
            schema_geotrek='public',
            schema_django='public',
        )
        context.update(context_settings)
        rendered_sql = template.render(context)
        cur.execute("DROP FUNCTION IF EXISTS path_deletion() CASCADE;")
        cur.execute(rendered_sql)

        cur.execute(f"DELETE FROM core_path WHERE id = {p1.pk}")
        cur.execute(f"DELETE FROM core_path WHERE id = {p2.pk}")

        self.assertEqual(Path.objects.count(), 1)

    @skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
    def test_delete_protected_allow_path(self):
        p1 = PathFactory.create()
        p2 = PathFactory.create()
        t = TrailFactory.create(paths=[p1, p2])

        # Everything should be all right before delete
        self.assertFalse(t.deleted)
        self.assertEqual(t.aggregations.count(), 2)

        p1.delete()
        t = Trail.objects.get(pk=t.pk)
        self.assertFalse(t.deleted)
        self.assertEqual(t.aggregations.count(), 1)

        with override_settings(ALLOW_PATH_DELETION_TOPOLOGY=False):
            with self.assertRaisesRegex(ProtectedError,
                                        "You can't delete this path, some topologies are linked with this path"):
                p2.delete()

        t = Trail.objects.get(pk=t.pk)
        self.assertFalse(t.deleted)
        self.assertEqual(t.aggregations.count(), 1)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class InterpolateTest(TestCase):
    def test_interpolate_not_saved(self):
        p = Path()
        with self.assertRaisesRegex(ValueError, "Cannot compute interpolation on unsaved path"):
            p.interpolate(Point(0, 0))

    def test_interpolate_reproj(self):
        p = PathFactory.create()
        self.assertEqual(p.interpolate(Point(3, 46.5, srid=4326)), (0, 0))


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class SnapTest(TestCase):
    def test_snap_not_saved(self):
        p = Path()
        with self.assertRaisesRegex(ValueError, "Cannot compute snap on unsaved path"):
            p.snap(Point(0, 0))

    def test_snap_reproj(self):
        p = PathFactory.create()
        snap = p.snap(Point(3, 46.5, srid=4326))
        self.assertEqual(snap.x, 700000)
        self.assertEqual(snap.y, 6600000)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class TrailTest(TestCase):
    def test_no_trail_csv(self):
        p1 = PathFactory.create()
        self.assertEqual(p1.trails_csv_display, 'None')

    def test_trail_csv(self):
        p1 = PathFactory.create()
        t1 = TrailFactory.create(paths=[p1])
        self.assertEqual(p1.trails_csv_display, t1.name)

    def test_trails_verbose_name(self):
        path = PathFactory.create()
        self.assertEqual(path.trails_verbose_name, 'Trails')

    def test_trails_duplicate(self):
        path_1 = PathFactory.create()
        path_2 = PathFactory.create()
        t = TrailFactory.create(paths=[path_1, path_2])
        self.assertEqual(Trail.objects.count(), 1)
        self.assertEqual(PathAggregation.objects.count(), 2)
        t.duplicate()
        self.assertEqual(PathAggregation.objects.count(), 4)
        self.assertEqual(Trail.objects.count(), 2)


class TrailTestDisplay(TestCase):

    def test_trails_certifications_display(self):
        t1 = TrailFactory.create()
        certif = CertificationTrailFactory.create(trail=t1)
        self.assertEqual(t1.certifications_display, f'{certif}')
        clear_internal_user_cache()
        certif_pk = certif.pk
        trail_pk = t1.pk
        obj_repr = str(t1)
        t1.delete(force=True)
        model_num = ContentType.objects.get_for_model(CertificationTrail).pk
        entry = LogEntry.objects.get(content_type=model_num, object_id=certif_pk)
        self.assertEqual(entry.change_message, f"Deleted by cascade from Trail {trail_pk} - {obj_repr}")
        self.assertEqual(entry.action_flag, DELETION)


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
class PathVisibilityTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.path = PathFactory()
        cls.invisible = PathFactory(visible=False)

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


@skipIf(not settings.TREKKING_TOPOLOGY_ENABLED, 'Test with dynamic segmentation only')
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
        self.assertFalse(p.check_path_not_overlap(p.geom, p.pk))
        # Overlaping twice
        p = PathFactory.create(geom=LineString((20, 1), (20, 0), (25, 0), (25, 1),
                                               (30, 1), (30, 0), (35, 0), (35, 1)))
        self.assertFalse(p.check_path_not_overlap(p.geom, p.pk))

        # But crossing is ok
        p = PathFactory.create(geom=LineString((6, 1), (6, 3)))
        self.assertTrue(p.check_path_not_overlap(p.geom, p.pk))
        # Touching is ok too
        p = PathFactory.create(geom=LineString((5, 1), (5, 0)))
        self.assertTrue(p.check_path_not_overlap(p.geom, p.pk))
        # Touching twice is ok too
        p = PathFactory.create(geom=LineString((2.5, 0), (3, 1), (3.5, 0)))
        self.assertTrue(p.check_path_not_overlap(p.geom, p.pk))

    def test_snapping(self):
        # Sinosoid line
        coords = [(x, math.sin(x)) for x in range(10)]
        PathFactory.create(geom=LineString(*coords))
        r"""
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


class ComfortTest(TestCase):
    def test_name_with_structure(self):
        structure = StructureFactory.create(name="structure")
        comfort = ComfortFactory.create(comfort="comfort", structure=structure)
        self.assertEqual("comfort (structure)", str(comfort))

    def test_name_without_structure(self):
        comfort = ComfortFactory.create(comfort="comfort")
        self.assertEqual("comfort", str(comfort))


class TrailCategory(TestCase):
    """Test trail category model"""
    def test_trail_category_name_with_structure(self):
        structure = StructureFactory.create(name="structure")
        trail_category = TrailCategoryFactory.create(label="My category", structure=structure)
        self.assertEqual("My category (structure)", str(trail_category))

    def test_trail_category_name_without_structure(self):
        trail_category = TrailCategoryFactory.create(label="My category")
        self.assertEqual("My category", str(trail_category))


class CertificationTest(TestCase):
    """Test certifications trail models"""

    @classmethod
    def setUpTestData(cls):
        cls.structure = StructureFactory.create(name="structure")
        cls.certification_label = CertificationLabelFactory.create(label="certification label")
        cls.certification_status = CertificationStatusFactory.create(label="certification status")

    def test_certification_label_name_with_structure(self):
        certification_label = CertificationLabelFactory.create(label="certification label", structure=self.structure)
        self.assertEqual("certification label (structure)", str(certification_label))

    def test_certification_label_name_without_structure(self):
        self.assertEqual("certification label", str(self.certification_label))

    def test_certification_status_name_with_structure(self):
        certification_status = CertificationStatusFactory.create(label="certification status", structure=self.structure)
        self.assertEqual("certification status (structure)", str(certification_status))

    def test_certification_status_name_without_structure(self):
        self.assertEqual("certification status", str(self.certification_status))

    def test_certification_name(self):
        certification_trail = CertificationTrailFactory.create(
            certification_label=self.certification_label,
            certification_status=self.certification_status,
        )
        self.assertEqual("certification label / certification status", str(certification_trail))
