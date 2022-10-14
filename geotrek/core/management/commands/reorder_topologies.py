from django.core.management.base import BaseCommand
from django.db import connection

from django.contrib.gis.geos import GEOSGeometry

from geotrek.core.models import PathAggregation, Topology


class Command(BaseCommand):
    help = """Reorder Pathaggregations of all topologies."""

    def handle(self, *args, **options):
        topologies = Topology.objects.all()
        for topology in topologies:
            cursor = connection.cursor()
            # We get all sublines of the topology
            cursor.execute(f"""
            SELECT ST_ASTEXT(ST_SmartLineSubstring(t.geom, et.start_position, et.end_position))
            FROM core_topology e, core_pathaggregation et, core_path t
            WHERE e.id = {topology.pk} AND et.topo_object_id = e.id AND et.path_id = t.id
            AND GeometryType(ST_SmartLineSubstring(t.geom, et.start_position, et.end_position)) != 'POINT'
            ORDER BY et."order", et.id
            """)
            geom_lines = cursor.fetchall()
            # We use ft_Smart_MakeLine to get the order of the lines
            cursor.execute(f"""SELECT * FROM ft_Smart_MakeLine(ARRAY{[geom[0] for geom in geom_lines]}::geometry[])""")
            # We remove first value (algorithme use a 0 by default to go through the lines and will always be here)
            # Then we need to remove first value and remove 1 to all of them because Path aggregation's orders begin at 0
            orders = [result - 1 for result in cursor.fetchall()[0][1][1:]]
            # We get all the Points that we didn't get for smart make line
            cursor = connection.cursor()
            cursor.execute(f"""
            SELECT ST_ASTEXT(ST_SmartLineSubstring(t.geom, et.start_position, et.end_position))
            FROM core_topology e, core_pathaggregation et, core_path t
            WHERE e.id = {topology.pk} AND et.topo_object_id = e.id AND et.path_id = t.id
            AND GeometryType(ST_SmartLineSubstring(t.geom, et.start_position, et.end_position)) = 'POINT'
            ORDER BY et."order", et.id
            """)
            geom_points = cursor.fetchall()
            new_orders = []
            order_point = 0
            number_points = 0
            id_order = 0
            for geom_point_wkt in geom_points:
                geom_point = GEOSGeometry(geom_point_wkt[0], srid=2154)
                while id_order < len(orders) - 1:
                    order_actual = orders[id_order]
                    order_next = orders[id_order + 1]
                    id_order += 1
                    # We check if the point is on the actual line's end_point and next line's start_point to get its position
                    actual_point_end = GEOSGeometry(geom_lines[order_actual][0], srid=2154).boundary[1]   # Get end point of the geometry
                    next_point_start = GEOSGeometry(geom_lines[order_next][0], srid=2154).boundary[0]  # Get start point of the geometry
                    if geom_point == actual_point_end == next_point_start:
                        # If we find it position :
                        # we get all orders gnerated with 'smart make line' after last point (or start_point) to the actual point
                        new_orders.extend([order + number_points for order in orders[order_point:id_order]])
                        # We add the point inside the list of orders
                        new_orders.append(id_order + number_points)
                        # We keep number of points added to add the value to lines orders and points orders in the next iteration
                        number_points += 1
                        order_point = id_order
                        # We get next point
                        break
            # We add all the lines orders after last points. If we have no point, we would get all lines in the order [0:)
            new_orders.extend([order + number_points for order in orders[order_point:]])

            pas = []
            # We update every order with new orders.
            # The query is always in the same order between django and sql (order by "order" and id)
            # Path aggregation will be created in this order too
            for pa_order, pa_id in enumerate(PathAggregation.objects.filter(topo_object=topology).order_by('order', 'id').values_list('id', flat=True)):
                pa = PathAggregation.objects.get(id=pa_id)
                pa.order = new_orders[pa_order]
                pas.append(pa)
            PathAggregation.objects.bulk_update(pas, ['order'])
