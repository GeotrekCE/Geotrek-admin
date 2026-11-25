import os
from io import StringIO
from unittest import mock

from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, LineString, Point
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import IntegrityError, connection
from django.test import TestCase, override_settings

from geotrek.authent.models import Structure
from geotrek.core.management.commands.loadpaths import Command as LoadPathsCommand
from geotrek.core.models import Path, PathAggregation
from geotrek.core.tests.factories import PathFactory, TopologyFactory
from geotrek.trekking.tests.factories import POIFactory


class RemoveDuplicatePathTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        geom_1 = LineString((0, 0), (1, 0), (2, 0))
        cls.p1 = Path.objects.create(name="First Path", geom=geom_1)
        cls.p2 = Path.objects.create(name="Second Path", geom=geom_1)

        geom_2 = LineString((0, 2), (1, 2), (2, 2))
        cls.p3 = Path.objects.create(name="Third Path", geom=geom_2)
        cls.p4 = Path.objects.create(name="Fourth Path", geom=geom_2)

        geom_3 = LineString((2, 2), (1, 2), (0, 2))
        cls.p5 = Path.objects.create(name="Fifth Path", geom=geom_3)

        geom_4 = LineString((4, 0), (6, 0))

        cls.p6 = Path.objects.create(name="Sixth Path", geom=geom_4)
        cls.p7 = Path.objects.create(name="Seventh Path", geom=geom_4)

        geom_5 = LineString((0, 6), (1, 6), (2, 6))

        cls.p8 = Path.objects.create(name="Eighth Path", geom=geom_5)
        cls.p9 = Path.objects.create(name="Nineth Path", geom=geom_5)

        POIFactory.create(name="POI1", paths=[(cls.p1, 0.5, 0.5)])
        POIFactory.create(name="POI2", paths=[(cls.p2, 0.5, 0.5)])
        POIFactory.create(name="POI3", paths=[(cls.p4, 0.5, 0.5)])

    def test_remove_duplicate_path(self):
        """
        This test check that we remove 1 of the duplicate path and keep ones with topologies.

                poi3 (only on p4)
        +-------o------+                    p5 is reversed.
        p3/p4/p5
                poi1/poi2
        +-------o------+        +--------+
        p1/p2                     p6

        We get at the end p1, p3, p5, p6.
        """
        output = StringIO()
        call_command("remove_duplicate_paths", verbosity=2, stdout=output)

        self.assertEqual(Path.objects.count(), 5)
        self.assertCountEqual(
            (self.p1, self.p3, self.p5, self.p6, self.p8), list(Path.objects.all())
        )
        self.assertIn("Deleting path", output.getvalue())
        self.assertIn("duplicate paths have been deleted", output.getvalue())

    def test_remove_duplicate_path_visible(self):
        """
        This test check that we remove 1 of the duplicate path and keep ones with topologies.

                poi3 (only on p4)
        +-------o------+                    p5 is reversed.
        p3/p4/p5

        +-------o------+        +--------+
        p1/p2   poi1/poi2       p6

        We get at the end p2, p3, p5, p6.
        """
        output = StringIO()
        self.p1.visible = False
        self.p1.save()
        # Will remove only p1 because not visible
        self.p3.visible = False
        self.p3.save()
        # will remove the second because both of them are not visible
        self.p4.visible = False
        self.p4.save()
        call_command("remove_duplicate_paths", verbosity=2, stdout=output)

        self.assertEqual(Path.include_invisible.count(), 5)
        self.assertEqual(Path.objects.count(), 4)
        self.assertCountEqual(
            (self.p2, self.p3, self.p5, self.p6, self.p8),
            list(Path.include_invisible.all()),
        )
        self.assertCountEqual(
            (self.p2, self.p5, self.p6, self.p8), list(Path.objects.all())
        )
        self.assertIn("Deleting path", output.getvalue())
        self.assertIn("duplicate paths have been deleted", output.getvalue())

    def test_remove_duplicate_path_fail(self):
        output = StringIO()
        with mock.patch("geotrek.core.models.Path.delete") as mock_delete:
            mock_delete.side_effect = Exception("An ERROR")
            call_command("remove_duplicate_paths", verbosity=2, stdout=output)
        self.assertIn("An ERROR", output.getvalue())
        self.assertEqual(Path.include_invisible.count(), 9)
        self.assertEqual(Path.objects.count(), 9)
        self.assertIn("0 duplicate paths have been deleted", output.getvalue())


class LoadPathsCommandTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.filename = os.path.join(os.path.dirname(__file__), "data", "paths.geojson")
        cls.structure = Structure.objects.create(name="huh")

    def test_load_paths_without_file(self):
        with self.assertRaisesRegex(
            CommandError, "Error: the following arguments are required: file_path"
        ):
            call_command("loadpaths")

    @override_settings(SRID=4326, SPATIAL_EXTENT=(5, 10.0, 5, 11))
    def test_load_paths_out_of_spatial_extent(self):
        call_command("loadpaths", self.filename, srid=4326, verbosity=0)
        self.assertEqual(Path.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -1, 1, 5))
    def test_load_paths_within_spatial_extent(self):
        call_command("loadpaths", self.filename, srid=4326, verbosity=0)
        self.assertEqual(Path.objects.count(), 1)
        value = Path.objects.first()
        self.assertEqual(value.name, "lulu")
        self.assertEqual(value.structure, self.structure)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -1, 1, 5))
    def test_load_paths_comments(self):
        output = StringIO()
        call_command(
            "loadpaths",
            self.filename,
            srid=4326,
            verbosity=2,
            comment=["comment", "foo"],
            stdout=output,
        )
        output = output.getvalue()
        self.assertEqual(Path.objects.count(), 1)
        value = Path.objects.first()
        self.assertEqual(value.name, "lulu")
        self.assertEqual(value.comments, "Comment 2</br>foo2")
        self.assertEqual(value.structure, self.structure)
        self.assertIn(f"The comment {value.comments} was added on {value.name}", output)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -1, 1, 5))
    def test_load_paths_intersect_spatial_extent(self):
        output = StringIO()
        call_command(
            "loadpaths", self.filename, "-i", srid=4326, verbosity=2, stdout=output
        )
        output = output.getvalue()
        self.assertIn(
            f"All paths in DataSource will be linked to the structure : {self.structure.name}",
            output,
        )
        self.assertEqual(Path.objects.count(), 1)
        path = Path.objects.first()
        self.assertIn(f"Create path with pk : {path.pk}", output)
        value = Path.objects.first()
        self.assertEqual(value.name, "lulu")
        self.assertEqual(value.structure, self.structure)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_intersect_spatial_extent_2(self):
        output = StringIO()
        call_command(
            "loadpaths", self.filename, "-i", srid=4326, verbosity=2, stdout=output
        )
        output = output.getvalue()
        self.assertIn(
            f"All paths in DataSource will be linked to the structure : {self.structure.name}",
            output,
        )
        self.assertEqual(Path.objects.count(), 2)
        paths = Path.objects.all()
        self.assertIn(f"Create path with pk : {paths[0].pk}", output)
        self.assertIn(f"Create path with pk : {paths[1].pk}", output)
        value = Path.objects.first()
        self.assertEqual(value.name, "lulu")
        self.assertEqual(value.structure, self.structure)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_not_within_spatial_extent(self):
        output = StringIO()
        filename = os.path.join(os.path.dirname(__file__), "data", "point.geojson")
        call_command(
            "loadpaths",
            filename,
            structure=self.structure.name,
            srid=4326,
            verbosity=2,
            stdout=output,
        )
        self.assertRegex(
            output.getvalue(),
            "Feature FID 0 in Layer<(point|OGRGeoJSON)>'s geometry is not a Linestring",
        )

    def test_load_paths_fail_bad_srid(self):
        filename = os.path.join(os.path.dirname(__file__), "data", "bad_srid.geojson")
        with self.assertRaisesRegex(
            CommandError, "SRID is not well configurate, change/add option srid"
        ):
            call_command("loadpaths", filename, verbosity=0)

    def test_load_paths_with_bad_structure(self):
        with self.assertRaisesRegex(
            CommandError, "Structure does not match with instance's structures"
        ):
            call_command("loadpaths", self.filename, structure="gr", verbosity=0)

    def test_load_paths_with_multiple_structure(self):
        Structure.objects.create(name="other_structure")
        with self.assertRaisesRegex(
            CommandError,
            "There are more than 1 structure and you didn't define the option structure\nUse --structure to define it",
        ):
            call_command("loadpaths", self.filename, verbosity=0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_dry(self):
        output = StringIO()
        call_command(
            "loadpaths", self.filename, "-i", dry=True, verbosity=2, stdout=output
        )
        self.assertIn("2 objects will be create, 0 objects failed;", output.getvalue())
        self.assertEqual(Path.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_fail_with_dry(self):
        filename = os.path.join(os.path.dirname(__file__), "data", "bad_path.geojson")
        output = StringIO()
        call_command("loadpaths", filename, "-i", dry=True, verbosity=2, stdout=output)
        self.assertIn("0 objects will be create, 1 objects failed;", output.getvalue())
        self.assertEqual(Path.objects.count(), 0)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, 0, 4, 2))
    def test_load_paths_fail_without_dry(self):
        filename = os.path.join(os.path.dirname(__file__), "data", "bad_path.geojson")
        output = StringIO()
        with self.assertRaises(IntegrityError):
            call_command("loadpaths", filename, "-i", verbosity=2, stdout=output)

    @override_settings(SRID=4326, SPATIAL_EXTENT=(-1, -1, 1, 5))
    def test_load_paths_within_spatial_extent_no_srid_geom(self):
        filename = os.path.join(os.path.dirname(__file__), "data", "paths_no_srid.shp")
        call_command("loadpaths", filename, srid=4326, verbosity=0)
        self.assertEqual(Path.objects.count(), 1)
        value = Path.objects.first()
        self.assertEqual(value.name, "lulu")
        self.assertEqual(value.structure, self.structure)

    def test_check_srid_geos_geometry_without_srid(self):
        cmd = LoadPathsCommand()
        geom = LineString((0, 0), (1, 1))
        cmd.check_srid(2154, geom)
        self.assertEqual(geom.srid, 2154)


class ReorderTopologiesPathAggregationTest(TestCase):
    r"""
    Topologies are created with disordered path aggregations (same "order" on several
    aggregations, holes in the numbering, duplicated waypoints).

    In the diagrams, the path network is drawn with / \ and -, and the topology
    going through it is drawn with #.
    """

    def assertRecursiveAlmostEqual(self, a, b):
        if type(a) is float:
            assert type(b) is float
            self.assertAlmostEqual(a, b)
        else:
            assert len(a) == len(b)
            for i in range(len(a)):
                self.assertRecursiveAlmostEqual(a[i], b[i])

    def assertOrders(self, topology, orders):
        self.assertEqual(
            list(
                PathAggregation.objects.filter(topo_object=topology)
                .order_by("order", "id")
                .values_list("order", flat=True)
            ),
            orders,
        )

    def create_path(self, *coords):
        return PathFactory.create(geom=LineString(*coords, srid=settings.SRID))

    def create_topology(self, aggregations, deleted=False):
        """
        Create a topology with the given path aggregations: a list of
        (path, start_position, end_position, order), in any order.
        """
        topology = TopologyFactory.create(paths=[])
        for path, start, end, order in aggregations:
            topology.add_path(path, start, end, order, reload=False)
        if deleted:
            topology.deleted = True
            topology.save()
        topology.refresh_from_db()
        return topology

    def create_x_network(self):
        r"""
        E                   D
          \               /
            \ 2_a   1_b /
              \       /
                \   /
                  C
                / 1_a2
              B
            /
          / 1_a1
        A

        A (700000, 6600000)   B (700045, 6600045)   C (700050, 6600050)
        D (700100, 6600100)   E (700000, 6600100)
        """
        self.path_1_a1 = self.create_path((700000, 6600000), (700045, 6600045))
        self.path_1_a2 = self.create_path((700045, 6600045), (700050, 6600050))
        self.path_1_b = self.create_path((700050, 6600050), (700100, 6600100))
        self.path_2_a = self.create_path((700000, 6600100), (700050, 6600050))

    def create_x_network_split_three_times(self):
        r"""
        E                   D
          \ 2_a1    1_b2  /
            \           F
              G       /
           2_a2 \   / 1_b1
                  C
                / 1_a2
              B
            / 1_a1
          /
        A

        A (700000, 6600000)   B (700035, 6600035)   C (700050, 6600050)
        D (700100, 6600100)   E (700000, 6600100)   F (700075, 6600075)
        G (700035, 6600065)
        """
        self.path_1_a1 = self.create_path((700000, 6600000), (700035, 6600035))
        self.path_1_a2 = self.create_path((700035, 6600035), (700050, 6600050))
        self.path_1_b1 = self.create_path((700050, 6600050), (700075, 6600075))
        self.path_1_b2 = self.create_path((700075, 6600075), (700100, 6600100))
        self.path_2_a1 = self.create_path((700000, 6600100), (700035, 6600065))
        self.path_2_a2 = self.create_path((700035, 6600065), (700050, 6600050))

    def get_geometries(self, topology):
        geometries = []
        for pathagg in topology.aggregations.all():
            cursor = connection.cursor()
            cursor.execute(f"""SELECT * FROM ST_ASEWKT(ST_SmartLineSubstring('{pathagg.path.geom.ewkt}'::geometry,
                                                                              {pathagg.start_position},
                                                                              {pathagg.end_position}
                                                       ))
            """)
            geom = cursor.fetchall()[0][0]
            geometries.append(GEOSGeometry(geom, srid=settings.SRID).ewkt)
        return geometries

    def test_no_ids_option(self):
        r"""
        When not using the --ids option, only non-deleted topologies should be processed.

        E                   D
          \               #
            \ 2_a   1_b #
              \       #
                \   #
                  C
                # 1_a2
              B
            #
          # 1_a1
        A

        Two similar topologies: A → B → C → D, with the orders 0, 0, 1.
        One of them is deleted.
        """
        self.create_x_network()
        aggregations = [
            (self.path_1_a1, 0, 1, 0),
            (self.path_1_a2, 0, 1, 0),
            (self.path_1_b, 0, 1, 1),
        ]
        existing_topo = self.create_topology(aggregations)
        deleted_topo = self.create_topology(aggregations, deleted=True)
        self.assertOrders(existing_topo, [0, 0, 1])
        self.assertOrders(deleted_topo, [0, 0, 1])

        # Run the command
        output = StringIO()
        call_command("reorder_topologies", stdout=output)

        # Check that only the non-deleted topology has been reordered
        self.assertEqual("1 topology has been updated\n", output.getvalue())
        self.assertOrders(existing_topo, [0, 1, 2])
        self.assertOrders(deleted_topo, [0, 0, 1])

    def test_ids_option(self):
        r"""
        When using the --ids option, only the given topologies should be processed (even if deleted).

        E                   D
          \               #
            \ 2_a   1_b #
              \       #
                \   #
                  C
                # 1_a2
              B
            #
          # 1_a1
        A

        Three similar topologies: A → B → C → D, with the orders 0, 0, 1.
        One of them is deleted, another one is not passed to the command.
        """
        self.create_x_network()
        aggregations = [
            (self.path_1_a1, 0, 1, 0),
            (self.path_1_a2, 0, 1, 0),
            (self.path_1_b, 0, 1, 1),
        ]
        ignored_topo = self.create_topology(aggregations)
        existing_topo = self.create_topology(aggregations)
        deleted_topo = self.create_topology(aggregations, deleted=True)
        for topo in [ignored_topo, existing_topo, deleted_topo]:
            self.assertOrders(topo, [0, 0, 1])

        # Run the command on the last two topologies
        output = StringIO()
        call_command(
            "reorder_topologies", stdout=output, ids=[existing_topo.pk, deleted_topo.pk]
        )

        # Check that only the last two topologies have been reordered
        self.assertEqual("2 topologies have been updated\n", output.getvalue())
        self.assertOrders(ignored_topo, [0, 0, 1])
        self.assertOrders(existing_topo, [0, 1, 2])
        self.assertOrders(deleted_topo, [0, 1, 2])

    def test_no_reorder_needed_one_path_aggregation(self):
        r"""
        E                   D
          \               /
            \ 2_a   1_b /
              \       /
                \   /
                  C
                / 1_a2
              B
            #
          # 1_a1
        A

        Topology: A → B, with a single path aggregation.
        """
        self.create_x_network()
        topo = self.create_topology([(self.path_1_a1, 0, 1, 0)])

        # Check its geometry and path aggregation
        self.assertTrue(topo.coupled)
        self.assertRecursiveAlmostEqual(
            LineString((700000, 6600000), (700045, 6600045), srid=settings.SRID),
            topo.geom,
        )
        self.assertOrders(topo, [0])

        # Run the command
        output = StringIO()
        call_command("reorder_topologies", stdout=output)
        self.assertEqual("0 topologies have been updated\n", output.getvalue())

        # Check that its geometry and path aggregations have not changed
        topo.refresh_from_db()
        self.assertTrue(topo.coupled)
        self.assertRecursiveAlmostEqual(
            LineString((700000, 6600000), (700045, 6600045), srid=settings.SRID),
            topo.geom,
        )
        self.assertOrders(topo, [0])

    def test_no_reorder_needed_several_path_aggregations(self):
        r"""
        E                   D
          \               #
            \ 2_a   1_b #
              \       #
                \   #
                  C
                # 1_a2
              B
            #
          # 1_a1
        A

        Topology: A → B → C → D, already in order (0, 1, 2).
        """
        self.create_x_network()
        topo = self.create_topology(
            [
                (self.path_1_a1, 0, 1, 0),
                (self.path_1_a2, 0, 1, 1),
                (self.path_1_b, 0, 1, 2),
            ]
        )

        # Check its geometry and path aggregations
        self.assertTrue(topo.coupled)
        self.assertRecursiveAlmostEqual(
            LineString(
                (700000, 6600000),
                (700045, 6600045),
                (700050, 6600050),
                (700100, 6600100),
                srid=settings.SRID,
            ),
            topo.geom,
        )
        self.assertOrders(topo, [0, 1, 2])

        # Run the command
        output = StringIO()
        call_command("reorder_topologies", stdout=output)
        self.assertEqual("0 topologies have been updated\n", output.getvalue())

        # Check that its geometry and path aggregations have not changed
        topo.refresh_from_db()
        self.assertTrue(topo.coupled)
        self.assertRecursiveAlmostEqual(
            LineString(
                (700000, 6600000),
                (700045, 6600045),
                (700050, 6600050),
                (700100, 6600100),
                srid=settings.SRID,
            ),
            topo.geom,
        )
        self.assertOrders(topo, [0, 1, 2])

    def test_reorder_duplicated_orders(self):
        r"""
        E                   D
          \               #
            \ 2_a   1_b #
              \       #
                \   #
                  C
                # 1_a2
              B
            #
          # 1_a1
        A

        Topology: A → B → C → D, with the orders 0, 0, 1.
        """
        self.create_x_network()
        topo = self.create_topology(
            [
                (self.path_1_a1, 0, 1, 0),
                (self.path_1_a2, 0, 1, 0),
                (self.path_1_b, 0, 1, 1),
            ]
        )

        # The topology is decoupled
        self.assertFalse(topo.coupled)
        self.assertOrders(topo, [0, 0, 1])

        # Run the reorder_topologies command
        call_command("reorder_topologies", verbosity=0)

        # Check its path aggregations
        geometries = self.get_geometries(topo)
        self.assertEqual(
            geometries,
            [
                LineString((700000, 6600000), (700045, 6600045), srid=2154).ewkt,
                LineString((700045, 6600045), (700050, 6600050), srid=2154).ewkt,
                LineString((700050, 6600050), (700100, 6600100), srid=2154).ewkt,
            ],
        )
        self.assertOrders(topo, [0, 1, 2])

        # The topology should be recoupled and its geometry should have been computed
        topo.refresh_from_db()
        self.assertTrue(topo.coupled)
        self.assertRecursiveAlmostEqual(
            LineString(
                (700000, 6600000),
                (700045, 6600045),
                (700050, 6600050),
                (700100, 6600100),
                srid=settings.SRID,
            ),
            topo.geom,
        )

    def test_reorder_return_trips_with_waypoints(self):
        r"""
        E                   D
          \               #
            \ 2_a   1_b #
              \       #
                \   #
                  C
                W1 1_a2
              B
            W2
          # 1_a1
        A

        W1 (700047.5, 6600047.5)   W2 (700025, 6600025)

        Topology: A → B → W1 → B → W2 → B → C → D, with two waypoints and two return
        trips. Each piece of line shares its order with the next one.
        """
        self.create_x_network()
        topo = self.create_topology(
            [
                (self.path_1_a1, 0, 1, 0),
                (self.path_1_a2, 0, 0.5, 0),
                (self.path_1_a2, 0.5, 0.5, 1),  # W1
                (self.path_1_a2, 0.5, 0, 2),
                (self.path_1_a1, 1, 25 / 45, 2),
                (self.path_1_a1, 25 / 45, 25 / 45, 3),  # W2
                (self.path_1_a1, 25 / 45, 1, 4),
                (self.path_1_a2, 0, 1, 4),
                (self.path_1_b, 0, 1, 5),
            ]
        )

        # The topology is decoupled
        self.assertFalse(topo.coupled)
        self.assertOrders(topo, [0, 0, 1, 2, 2, 3, 4, 4, 5])

        # Run the reorder_topologies command
        call_command("reorder_topologies", verbosity=0)

        # Check its path aggregations
        geometries = self.get_geometries(topo)
        self.assertEqual(
            geometries,
            [
                LineString((700000, 6600000), (700045, 6600045), srid=2154).ewkt,
                LineString((700045, 6600045), (700047.5, 6600047.5), srid=2154).ewkt,
                Point(700047.5, 6600047.5, srid=2154).ewkt,
                LineString((700047.5, 6600047.5), (700045, 6600045), srid=2154).ewkt,
                LineString((700045, 6600045), (700025, 6600025), srid=2154).ewkt,
                Point(700025, 6600025, srid=2154).ewkt,
                LineString((700025, 6600025), (700045, 6600045), srid=2154).ewkt,
                LineString((700045, 6600045), (700050, 6600050), srid=2154).ewkt,
                LineString((700050, 6600050), (700100, 6600100), srid=2154).ewkt,
            ],
        )
        self.assertOrders(topo, [0, 1, 2, 3, 4, 5, 6, 7, 8])

        # The topology should be recoupled and its geometry should have been computed
        topo.refresh_from_db()
        self.assertTrue(topo.coupled)
        self.assertRecursiveAlmostEqual(
            LineString(
                (700000, 6600000),
                (700045, 6600045),
                (700047.5, 6600047.5),
                (700045, 6600045),
                (700025, 6600025),
                (700045, 6600045),
                (700050, 6600050),
                (700100, 6600100),
                srid=settings.SRID,
            ),
            topo.geom,
        )

    def test_reorder_return_trip_on_another_branch_with_waypoint(self):
        """
        E                   D
          W 2_a1    1_b2  #
            #           F
              G       #
           2_a2 #   # 1_b1
                  C
                # 1_a2
              B
            # 1_a1
          #
        A

        W (700005, 6600095)

        Topology: A → B → C → G → W → G → C → F → D, with a return trip on the branch
        2_a up to the waypoint W. Each piece of line shares its order with the next one.
        """
        self.create_x_network_split_three_times()
        topo = self.create_topology(
            [
                (self.path_1_a1, 0, 1, 0),
                (self.path_1_a2, 0, 1, 0),
                (self.path_2_a2, 1, 0, 1),
                (self.path_2_a1, 1, 1 / 7, 1),
                (self.path_2_a1, 1 / 7, 1 / 7, 2),  # W
                (self.path_2_a1, 1 / 7, 1, 3),
                (self.path_2_a2, 0, 1, 3),
                (self.path_1_b1, 0, 1, 4),
                (self.path_1_b2, 0, 1, 4),
            ]
        )

        # The topology is decoupled
        self.assertFalse(topo.coupled)
        self.assertOrders(topo, [0, 0, 1, 1, 2, 3, 3, 4, 4])

        # Run the reorder_topologies command
        call_command("reorder_topologies", verbosity=0)

        # Check its path aggregations
        geometries = self.get_geometries(topo)
        self.assertEqual(
            geometries,
            [
                LineString((700000, 6600000), (700035, 6600035), srid=2154).ewkt,
                LineString((700035, 6600035), (700050, 6600050), srid=2154).ewkt,
                LineString((700050, 6600050), (700035, 6600065), srid=2154).ewkt,
                LineString((700035, 6600065), (700005, 6600095), srid=2154).ewkt,
                Point(700005, 6600095, srid=2154).ewkt,
                LineString((700005, 6600095), (700035, 6600065), srid=2154).ewkt,
                LineString((700035, 6600065), (700050, 6600050), srid=2154).ewkt,
                LineString((700050, 6600050), (700075, 6600075), srid=2154).ewkt,
                LineString((700075, 6600075), (700100, 6600100), srid=2154).ewkt,
            ],
        )
        self.assertOrders(topo, [0, 1, 2, 3, 4, 5, 6, 7, 8])

        # The topology should be recoupled and its geometry should have been computed
        topo.refresh_from_db()
        self.assertTrue(topo.coupled)
        self.assertRecursiveAlmostEqual(
            LineString(
                (700000, 6600000),
                (700035, 6600035),
                (700050, 6600050),
                (700035, 6600065),
                (700005, 6600095),
                (700035, 6600065),
                (700050, 6600050),
                (700075, 6600075),
                (700100, 6600100),
                srid=settings.SRID,
            ),
            topo.geom,
        )

    def test_reorder_return_trip_on_another_branch_without_waypoint(self):
        r"""
        E                   D
          \ 2_a1    1_b2  #
            \           F
              G       #
           2_a2 #   # 1_b1
                  C
                # 1_a2
              B
            # 1_a1
          #
        A

        Topology: A → B → C → G → C → F → D, with a return trip on 2_a2 and no waypoint.
        The orders are duplicated and have a hole.
        """
        self.create_x_network_split_three_times()
        topo = self.create_topology(
            [
                (self.path_1_a1, 0, 1, 0),
                (self.path_1_a2, 0, 1, 0),
                (self.path_2_a2, 1, 0, 1),
                (self.path_2_a2, 0, 1, 3),
                (self.path_1_b1, 0, 1, 4),
                (self.path_1_b2, 0, 1, 4),
            ]
        )

        # The topology is decoupled
        self.assertFalse(topo.coupled)
        self.assertOrders(topo, [0, 0, 1, 3, 4, 4])

        # Run the reorder_topologies command
        call_command("reorder_topologies", verbosity=0)

        # Check its path aggregations
        geometries = self.get_geometries(topo)
        self.assertEqual(
            geometries,
            [
                LineString((700000, 6600000), (700035, 6600035), srid=2154).ewkt,
                LineString((700035, 6600035), (700050, 6600050), srid=2154).ewkt,
                LineString((700050, 6600050), (700035, 6600065), srid=2154).ewkt,
                LineString((700035, 6600065), (700050, 6600050), srid=2154).ewkt,
                LineString((700050, 6600050), (700075, 6600075), srid=2154).ewkt,
                LineString((700075, 6600075), (700100, 6600100), srid=2154).ewkt,
            ],
        )
        self.assertOrders(topo, [0, 1, 2, 3, 4, 5])

        # The topology should be recoupled and its geometry should have been computed
        topo.refresh_from_db()
        self.assertTrue(topo.coupled)
        self.assertRecursiveAlmostEqual(
            LineString(
                (700000, 6600000),
                (700035, 6600035),
                (700050, 6600050),
                (700035, 6600065),
                (700050, 6600050),
                (700075, 6600075),
                (700100, 6600100),
                srid=settings.SRID,
            ),
            topo.geom,
        )

    def test_reorder_duplicated_waypoints_on_a_node(self):
        r"""
        Network: the path 1_b loops back from D to the node W, where the path 2_a is split.

        E         H---------D
          \    /          /
            W           /
           /  \       /
         /      \   /
        I         C
                /
              /
            /
          /
        A

        1_a: A-C   2_a1: E-W   2_a2: W-C   1_b1: C-D-H-W   1_b2: W-I
        A (700000, 6600000)   C (700050, 6600050)   D (700100, 6600100)
        E (700000, 6600100)   H (700050, 6600100)   I (700000, 6600050)
        W (700025, 6600075)

        Topology:

        E         H#########D
          \    #          #
            W           #
           #  #       #
         #      #   #
        I         C
                #
              #
            #
          #
        A

        A → C → W → C → D → H → W → I
        The waypoint W is duplicated on every path of its node.
        Each piece of line shares its order with the next one.
        """
        path_1_a = self.create_path((700000, 6600000), (700050, 6600050))
        path_2_a1 = self.create_path((700000, 6600100), (700025, 6600075))
        path_2_a2 = self.create_path((700025, 6600075), (700050, 6600050))
        path_1_b1 = self.create_path(
            (700050, 6600050), (700100, 6600100), (700050, 6600100), (700025, 6600075)
        )
        path_1_b2 = self.create_path((700025, 6600075), (700000, 6600050))
        topo = self.create_topology(
            [
                (path_1_a, 0, 1, 0),
                (path_2_a2, 1, 0, 1),
                (path_2_a1, 1, 1, 1),  # W
                (path_2_a2, 0, 0, 2),  # W
                (path_1_b1, 1, 1, 2),  # W
                (path_1_b2, 0, 0, 2),  # W
                (path_2_a2, 0, 1, 3),
                (path_1_b1, 0, 1, 4),
                (path_1_b2, 0, 1, 4),
            ]
        )

        # The topology is decoupled
        self.assertFalse(topo.coupled)
        self.assertOrders(topo, [0, 1, 1, 2, 2, 2, 3, 4, 4])

        # Run the reorder_topologies command
        call_command("reorder_topologies", verbosity=0)

        # Check its path aggregations: the waypoint is kept once between each pair of lines
        geometries = self.get_geometries(topo)
        self.assertEqual(
            geometries,
            [
                LineString((700000, 6600000), (700050, 6600050), srid=2154).ewkt,
                LineString((700050, 6600050), (700025, 6600075), srid=2154).ewkt,
                Point(700025, 6600075, srid=2154).ewkt,
                LineString((700025, 6600075), (700050, 6600050), srid=2154).ewkt,
                LineString(
                    (700050, 6600050),
                    (700100, 6600100),
                    (700050, 6600100),
                    (700025, 6600075),
                    srid=2154,
                ).ewkt,
                Point(700025, 6600075, srid=2154).ewkt,
                LineString((700025, 6600075), (700000, 6600050), srid=2154).ewkt,
            ],
        )
        self.assertOrders(topo, [0, 1, 2, 3, 4, 5, 6])

        # The topology should be recoupled and its geometry should have been computed
        topo.refresh_from_db()
        self.assertTrue(topo.coupled)
        self.assertRecursiveAlmostEqual(
            LineString(
                (700000, 6600000),
                (700050, 6600050),
                (700025, 6600075),
                (700050, 6600050),
                (700100, 6600100),
                (700050, 6600100),
                (700025, 6600075),
                (700000, 6600050),
                srid=settings.SRID,
            ),
            topo.geom,
        )

    def test_reorder_fail_because_of_missing_path_aggregation(self):
        r"""
        E                   D
          \               #
            \ 2_a   1_b #
              W       #
                #   #
                  C
                # 1_a2
              B
            #
          # 1_a1
        A

        W (700025, 6600075)

        Topology: A → B → C → W … C → D. The way back from the waypoint W to C is
        missing, so the pieces of line cannot be chained and the command must fail.
        """
        self.create_x_network()
        topo = self.create_topology(
            [
                (self.path_1_a1, 0, 1, 0),
                (self.path_1_a2, 0, 1, 0),
                (self.path_2_a, 1, 0.5, 1),
                (self.path_2_a, 0.5, 0.5, 2),  # W
                (self.path_1_b, 0, 1, 4),
            ]
        )

        # The topology is decoupled
        self.assertFalse(topo.coupled)
        self.assertOrders(topo, [0, 0, 1, 2, 4])

        # Run the reorder_topologies command: it should fail
        output = StringIO()
        call_command("reorder_topologies", stdout=output)
        self.assertIn(
            f"Topologies with errors:\n{topo.kind} id: {topo.pk}\n", output.getvalue()
        )

        # Check that its path aggregations have not changed
        topo.refresh_from_db()
        self.assertFalse(topo.coupled)
        self.assertOrders(topo, [0, 0, 1, 2, 4])


class MergePathsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        geom_1 = LineString((0, 0), (1, 1))
        cls.p1 = Path.objects.create(geom=geom_1)
        geom_2 = LineString((1, 1), (2, 2))
        cls.p2 = Path.objects.create(geom=geom_2)
        geom_3 = LineString((2, 2), (3, 3))
        cls.p3 = Path.objects.create(geom=geom_3)
        geom_4 = LineString((2, 2), (6, 1))
        cls.p4 = Path.objects.create(geom=geom_4)
        geom_5 = LineString((3, 3), (4, 4))
        cls.p5 = Path.objects.create(geom=geom_5)
        geom_6 = LineString((4, 4), (5, 5))
        cls.p6 = Path.objects.create(geom=geom_6)
        geom_7 = LineString((5, 5), (6, 6))
        cls.p7 = Path.objects.create(geom=geom_7)
        geom_8 = LineString((6, 6), (7, 7))
        cls.p8 = Path.objects.create(geom=geom_8)
        geom_9 = LineString((7, 7), (8, 8))
        cls.p9 = Path.objects.create(geom=geom_9)
        geom_10 = LineString((6, 1), (4, 1))
        cls.p10 = Path.objects.create(geom=geom_10)
        geom_11 = LineString((4, 1), (4, 0))
        cls.p11 = Path.objects.create(geom=geom_11)
        geom_12 = LineString((4, 1), (6, 1))
        cls.p12 = Path.objects.create(geom=geom_12)
        geom_13 = LineString((6, 6), (7, 5))
        cls.p13 = Path.objects.create(geom=geom_13)
        geom_14 = LineString((8, 8), (9, 9))
        cls.p14 = Path.objects.create(geom=geom_14)
        geom_15 = LineString((5, 3), (4, 1))
        cls.p15 = Path.objects.create(geom=geom_15)
        geom_16 = LineString((7, 5), (8, 5), (8, 6), (7, 6), (7, 5))
        cls.p16 = Path.objects.create(geom=geom_16)

    @override_settings(PATH_SNAPPING_DISTANCE=0, PATH_MERGE_SNAPPING_DISTANCE=0)
    def test_find_and_merge_paths(self):
        # Before call
        #    p1      p2      p3      p5     p6     p7      p8     p9     p14
        # +-------+------+-------+------+-------+------+-------+------+------+
        #                |                             |
        #                |  p4                         |  p13
        #                |                             |
        #                +                             +-------
        #                |                             |       |
        #                |  p10                        |   p16 |
        #          p11   |                             |       |
        #         +------+------+ p15                  --------
        #                |
        #                |  p12
        #                |
        #                +
        self.assertEqual(Path.objects.count(), 16)
        output = StringIO()
        call_command("merge_segmented_paths", stdout=output)
        # After call
        #        p1                     p6                       p14
        # +--------------+-----------------------------+---------------------+
        #                |                             |
        #                |  p4                         |  p13
        #                |                             |
        #                +                             +-------
        #                |                             |       |
        #                |  p10                        |   p16 |
        #          p11   |                             |       |
        #         +------+------+ p15                  --------
        #                |
        #                |  p12
        #                |
        #
        output_str = (
            f"┌ STEP 1\n"
            f"├ Merged {self.p2.pk} into {self.p1.pk}\n"
            f"├ Merged {self.p9.pk} into {self.p14.pk}\n"
            f"├ Cannot merge {self.p16.pk} and {self.p13.pk}\n"
            f"├ Merged {self.p8.pk} into {self.p14.pk}\n"
            f"├ Already discarded {self.p16.pk} and {self.p13.pk}\n"
            f"└ 3 merges\n"
            f"┌ STEP 2\n"
            f"├ Cannot merge {self.p1.pk} and {self.p3.pk}\n"
            f"├ Merged {self.p3.pk} into {self.p5.pk}\n"
            f"├ Merged {self.p5.pk} into {self.p6.pk}\n"
            f"├ Cannot merge {self.p14.pk} and {self.p7.pk}\n"
            f"└ 2 merges\n"
            f"┌ STEP 3\n"
            f"├ Cannot merge {self.p6.pk} and {self.p1.pk}\n"
            f"├ Cannot merge {self.p6.pk} and {self.p4.pk}\n"
            f"├ Merged {self.p7.pk} into {self.p6.pk}\n"
            f"├ Cannot merge {self.p7.pk} and {self.p6.pk}\n"
            f"├ Cannot merge {self.p7.pk} and {self.p13.pk}\n"
            f"├ Already discarded {self.p7.pk} and {self.p14.pk}\n"
            f"├ Cannot merge {self.p10.pk} and {self.p4.pk}\n"
            f"├ Cannot merge {self.p10.pk} and {self.p11.pk}\n"
            f"├ Cannot merge {self.p10.pk} and {self.p15.pk}\n"
            f"├ Cannot merge {self.p12.pk} and {self.p4.pk}\n"
            f"├ Cannot merge {self.p12.pk} and {self.p11.pk}\n"
            f"├ Cannot merge {self.p12.pk} and {self.p15.pk}\n"
            f"├ Already discarded {self.p13.pk} and {self.p7.pk}\n"
            f"├ Cannot merge {self.p13.pk} and {self.p14.pk}\n"
            f"├ Already discarded {self.p13.pk} and {self.p16.pk}\n"
            f"└ 1 merges\n"
            f"\n"
            f"--- RAN 6 MERGES - FROM 16 TO 10 PATHS ---\n"
        )
        self.assertEqual(Path.objects.count(), 10)
        self.assertIn(output_str, output.getvalue())


class GeneratePgrNetworkTopologyTest(TestCase):
    def test_generate_network_topology(self):
        """Checks that the graph data is generated when running the command."""
        geom_1 = LineString(
            Point(700000, 6600000), Point(700100, 6600100), srid=settings.SRID
        )
        geom_2 = LineString(
            Point(700000, 6600100), Point(700100, 6600000), srid=settings.SRID
        )
        path_1 = PathFactory.create(geom=geom_1)
        path_2 = PathFactory.create(geom=geom_2)
        call_command("generate_pgr_network_topology")
        path_1.refresh_from_db()
        path_2.refresh_from_db()
        self.assertIsNotNone(path_1.source_pgr)
        self.assertIsNotNone(path_1.target_pgr)
        self.assertIsNotNone(path_2.source_pgr)
        self.assertIsNotNone(path_2.target_pgr)

    def test_regenerate_network_topology_with_flush(self):
        """Checks that running the command with the flush option updates obsolete graph data and populates missing data."""
        geom_1 = LineString(
            Point(700000, 6600000), Point(700100, 6600100), srid=settings.SRID
        )
        geom_2 = LineString(
            Point(700000, 6600100), Point(700100, 6600000), srid=settings.SRID
        )
        path_1 = PathFactory.create(geom=geom_1)
        path_2 = PathFactory.create(geom=geom_2)

        # Simulate obsolete data for path_1, which should be overwritten thanks to the flush option:
        obsolete_path_1_source = 4653
        obsolete_path_1_target = 4654
        cursor = connection.cursor()
        query = """UPDATE core_path SET source = %s, target = %s WHERE id = %s"""
        cursor.execute(
            query, [obsolete_path_1_source, obsolete_path_1_target, path_1.pk]
        )
        path_1.refresh_from_db()
        path_2.refresh_from_db()
        self.assertEqual(path_1.source_pgr, obsolete_path_1_source)
        self.assertEqual(path_1.target_pgr, obsolete_path_1_target)
        self.assertIsNone(path_2.source_pgr)
        self.assertIsNone(path_2.target_pgr)

        # Run the command and check the graph data
        call_command("generate_pgr_network_topology", "--flush")
        path_1.refresh_from_db()
        path_2.refresh_from_db()
        self.assertNotEqual(path_1.source_pgr, obsolete_path_1_source)
        self.assertNotEqual(path_1.target_pgr, obsolete_path_1_target)
        self.assertIsNotNone(path_2.source_pgr)
        self.assertIsNotNone(path_2.target_pgr)

    def test_regenerating_network_topology_with_flush_clears_draft_or_invisible_paths(
        self,
    ):
        """Checks that running the command with the flush option clears data for draft or invisible paths."""
        geom_1 = LineString(
            Point(700000, 6600000), Point(700100, 6600100), srid=settings.SRID
        )
        geom_2 = LineString(
            Point(700000, 6600100), Point(700100, 6600000), srid=settings.SRID
        )
        path_1 = PathFactory.create(geom=geom_1, draft=True)
        path_2 = PathFactory.create(geom=geom_2, visible=False)

        # Simulate obsolete data for both paths. This data should be cleared thanks to the flush option:
        cursor = connection.cursor()
        query = """UPDATE core_path SET source = %s, target = %s WHERE id = %s"""
        cursor.execute(query, [1, 2, path_1.pk])
        cursor.execute(query, [3, 4, path_2.pk])
        path_1.refresh_from_db()
        path_2.refresh_from_db()
        self.assertEqual(path_1.source_pgr, 1)
        self.assertEqual(path_1.target_pgr, 2)
        self.assertEqual(path_2.source_pgr, 3)
        self.assertEqual(path_2.target_pgr, 4)

        # Run the command and check the graph data
        call_command("generate_pgr_network_topology", "--flush")
        path_1.refresh_from_db()
        path_2.refresh_from_db()
        self.assertIsNone(path_1.source_pgr)
        self.assertIsNone(path_1.target_pgr)
        self.assertIsNone(path_2.source_pgr)
        self.assertIsNone(path_2.target_pgr)
