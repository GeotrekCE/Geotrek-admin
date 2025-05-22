from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import OneToOneRel

from geotrek.core.models import PathAggregation, Topology


class Command(BaseCommand):
    help = """Reorder Pathaggregations of all topologies."""

    def get_geom_lines(self, topology):
        cursor = connection.cursor()
        # We get all sublines of the topology
        cursor.execute(f"""
                    SELECT et.id, ST_ASTEXT(ST_SmartLineSubstring(t.geom, et.start_position, et.end_position))
                    FROM core_topology e, core_pathaggregation et, core_path t
                    WHERE e.id = {topology.pk} AND et.topo_object_id = e.id AND et.path_id = t.id
                    AND GeometryType(ST_SmartLineSubstring(t.geom, et.start_position, et.end_position)) != 'POINT'
                    ORDER BY et."order", et.id
                    """)
        geom_lines_order = cursor.fetchall()
        return geom_lines_order

    def get_new_order(self, geom_lines):
        cursor = connection.cursor()
        # We use ft_Smart_MakeLine to get the order of the lines
        cursor.execute(
            f"""SELECT * FROM ft_Smart_MakeLine(ARRAY{[geom[1] for geom in geom_lines]}::geometry[])"""
        )

        # We remove first value (algorithme use a 0 by default to go through the lines and will always be here)
        # Then we need to remove first value and remove 1 to all of them because Path aggregation's orders begin at 0
        fetched = cursor.fetchall()
        return fetched[0][1]

    def handle(self, *args, **options):
        topologies = Topology.objects.filter(deleted=False)
        failed_topologies = []
        num_updated_topologies = 0
        for topology in topologies:
            geom_lines = self.get_geom_lines(topology)

            new_order = self.get_new_order(geom_lines)
            if new_order == [] or (
                len(geom_lines) >= 2 and geom_lines[1][1] == "LINESTRING EMPTY"
            ):
                for field in topology._meta.get_fields():
                    if isinstance(field, OneToOneRel) and hasattr(topology, field.name):
                        failed_topologies.append(
                            str(
                                f"{getattr(topology, field.name).kind} id: {topology.pk}"
                            )
                        )

            if len(new_order) <= 2 or (
                len(geom_lines) >= 2 and geom_lines[1][1] == "LINESTRING EMPTY"
            ):
                continue
            order_maked_lines = new_order[1:]
            orders = [result - 1 for result in order_maked_lines]
            new_orders = {}
            for x, geom_line in enumerate(geom_lines):
                new_orders[geom_line[0]] = orders[x]

            # We generate a dict with id Pathaggregation as key and new order (without points)

            # We get all the Points that we didn't get for smart make line
            cursor = connection.cursor()
            cursor.execute(f"""
            SELECT et.id, ST_ASTEXT(ST_SmartLineSubstring(t.geom, et.start_position, et.end_position))
            FROM core_topology e, core_pathaggregation et, core_path t
            WHERE e.id = {topology.pk} AND et.topo_object_id = e.id AND et.path_id = t.id
            AND GeometryType(ST_SmartLineSubstring(t.geom, et.start_position, et.end_position)) = 'POINT'
            ORDER BY et."order", et.id
            """)
            points = cursor.fetchall()
            id_order = 0

            dict_points = {}
            for id_pa_point, geom_point_wkt in points:
                dict_points[id_pa_point] = GEOSGeometry(
                    geom_point_wkt, srid=settings.SRID
                )

            points_touching = {}
            # Find points aggregations that touches lines
            while id_order < len(orders) - 1:
                geometries_points = dict_points.values()
                order_actual = orders[id_order]
                order_next = orders[id_order + 1]
                actual_point_end = GEOSGeometry(
                    geom_lines[order_actual][1], srid=settings.SRID
                ).boundary[1]  # Get end point of the geometry
                next_point_start = GEOSGeometry(
                    geom_lines[order_next][1], srid=settings.SRID
                ).boundary[0]  # Get start point of the geometry
                if (
                    actual_point_end == next_point_start
                    and actual_point_end in geometries_points
                ):
                    for id_pa_point, point_geom in dict_points.items():
                        if point_geom == actual_point_end:
                            points_touching[id_pa_point] = id_order + 1
                            dict_points.pop(id_pa_point)
                            break
                id_order += 1

            points_added = 0
            # We add all points between the lines and remove points generated which should not be here (it happens)
            for id_pa_point, order_point_touching in points_touching.items():
                new_orders = {
                    id_pa: new_order + 1
                    if new_order >= order_point_touching + points_added
                    else new_order
                    for id_pa, new_order in new_orders.items()
                }
                new_orders[id_pa_point] = order_point_touching + points_added
                points_added += 1
            PathAggregation.objects.filter(topo_object=topology).exclude(
                id__in=new_orders.keys()
            ).delete()

            initial_order = PathAggregation.objects.filter(
                topo_object=topology
            ).values_list("id", flat=True)

            pas_updated = []
            for pa_id in initial_order:
                pa = PathAggregation.objects.get(id=pa_id)
                if pa.order != new_orders[pa_id]:
                    pa.order = new_orders[pa_id]
                    pas_updated.append(pa)
            PathAggregation.objects.bulk_update(pas_updated, ["order"])
            if pas_updated:
                num_updated_topologies += 1

        if options["verbosity"]:
            self.stdout.write(f"{num_updated_topologies} topologies has beeen updated")

        if options["verbosity"] and failed_topologies:
            self.stdout.write("Topologies with errors :")
            self.stdout.write("\n".join(failed_topologies))
