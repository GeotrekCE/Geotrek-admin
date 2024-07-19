import json

from django.db import connection
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, Point, LineString, MultiLineString, GeometryCollection

from geotrek.common.utils import sqlfunction
from .models import Path


class PathRouter:
    def __init__(self):
        self.set_path_network_topology()

    def set_path_network_topology(self):
        """ Builds or updates the network topology """
        cursor = connection.cursor()
        query = """
                SELECT
                    pgr_createTopology(
                        'core_path',
                        0.00001,
                        'geom',
                        'id'
                    )
                """
        cursor.execute(query)
        return ('OK',) == cursor.fetchone()

    def get_route(self, steps):
        """
        Returns the whole route geojson and topology. Both of them is an array
        with each element being a sub-route from one step to another.
        """
        self.steps = steps
        self.steps_topo = [self.get_snapped_point_info(step) for step in steps]
        line_strings, serialized_topology = self.compute_all_steps_routes()
        if line_strings == []:
            return None

        multi_line_string = GeometryCollection(line_strings, srid=settings.SRID)
        multi_line_string.transform(settings.API_SRID)
        geojson = json.loads(multi_line_string.geojson)

        return {'geojson': geojson, 'serialized': serialized_topology}

    def get_snapped_point_info(self, latlng):
        """
        For one latlng, returns its closest path's id and its position on it.
        """
        # Transform the point to the right SRID
        point = Point(latlng.get('lng'), latlng.get('lat'), srid=settings.API_SRID)
        point.transform(settings.SRID)
        # Get the closest path
        # TODO: use an SQL function to get the closest path?
        closest_path = Path.closest(point)
        # Get which fraction of the Path this point is on
        closest_path_geom = f"'{closest_path.geom}'"
        point_geom = f"'{point.ewkt}'"
        fraction_of_distance = sqlfunction('SELECT ST_LineLocatePoint',
                                           closest_path_geom, point_geom)[0]
        return {
            'edge_id': closest_path.pk,
            'fraction': fraction_of_distance
        }

    def compute_all_steps_routes(self):
        all_steps_geometries = []  # Each elem is a linestring from one step to another
        all_steps_topologies = []  # Each elem is the topology from one step to another
        # Compute the shortest path for each pair of adjacent steps
        for i in range(len(self.steps_topo) - 1):
            from_step = self.steps_topo[i]
            to_step = self.steps_topo[i + 1]
            # Get the linestrings (segments of paths) between those two steps,
            # then merge them into one
            one_step_geometry, topology = self.get_two_steps_route(from_step, to_step)
            all_steps_topologies.append(topology)
            if one_step_geometry is None:
                return [], []
            print("one_step_geometry", one_step_geometry)
            print("topology", topology)
            all_steps_geometries.append(one_step_geometry)
        return all_steps_geometries, all_steps_topologies

    def get_two_steps_route(self, from_step, to_step):
        """
        Parameters:
            from_step ({edge_id: int, fraction: float})
            to_step ({edge_id: int, fraction: float})
        """
        from_edge_id = from_step.get('edge_id')
        to_edge_id = to_step.get('edge_id')

        if from_edge_id == to_edge_id:
            from_fraction = from_step.get('fraction')
            to_fraction = to_step.get('fraction')
            # If both points are on same edge, split it from the 1st to the 2nd
            path_substring = self.create_path_substring(
                from_edge_id,
                from_fraction,
                to_fraction
            )
            line_strings = [path_substring]
            topology = {
                'positions': {'0': [from_fraction, to_fraction]},
                'paths': [from_edge_id],
            }
        else:
            # Compute the shortest path between the two points
            line_strings, topology = self.compute_two_steps_route(from_step, to_step)

        step_geometry = self.merge_line_strings(line_strings)
        return step_geometry, topology

    def compute_two_steps_route(self, from_step, to_step):
        query = """
                WITH points as (
                    -- This is a virtual table of the points (start and end)
                    -- and their position on the closest edge
                    SELECT
                        points.pid,
                        points.edge_id,
                        points.fraction_start,
                        points.fraction_end,
                        -- TODO: use ST_SmartLineSubstring?
                        ST_LineSubstring(
                            core_path.geom,
                            points.fraction_start,
                            points.fraction_end
                        ) AS geom
                    FROM
                        (VALUES
                            (1, %s, 0, %s::float),
                            (1, %s, %s::float, 1),
                            (2, %s, 0, %s::float),
                            (2, %s, %s::float, 1)
                        ) AS points(pid, edge_id, fraction_start, fraction_end)
                        JOIN core_path ON core_path.id = points.edge_id
                ),

                pgr AS (
                    -- Get the route from point 1 to point 2 using pgr_withPoints.
                    -- next_node, prev_geom and next_geom will be used later
                    -- to reconstruct the final geometry of the shortest path.
                    SELECT
                        pgr.path_seq,
                        pgr.node,
                        pgr.edge,
                        core_path.geom as edge_geom,
                        (LEAD(pgr.node) OVER (ORDER BY path_seq)) AS next_node,
                        (LAG(core_path.geom) OVER (ORDER BY path_seq)) AS prev_geom,
                        (LEAD(core_path.geom) OVER (ORDER BY path_seq)) AS next_geom
                    FROM
                        pgr_withPoints(
                            'SELECT
                                id,
                                source,
                                target,
                                length as cost,
                                length as reverse_cost
                            FROM core_path
                            ORDER by id',
                            'SELECT *
                            FROM (
                                VALUES
                                    (1, %s, %s::float),
                                    (2, %s, %s::float)
                                ) AS points (pid, edge_id, fraction)',
                            -1, -2
                        ) as pgr
                        JOIN core_path ON core_path.id = pgr.edge
                ),

                route_geometry AS (
                    -- Reconstruct the geometry edge by edge.
                    -- At point 1 and 2, we get a portion of the edge.
                    SELECT
                        CASE
                        WHEN node = -1 THEN  -- Start point
                            (SELECT points.geom
                                FROM points
                                -- Get the edge portion that leads to the next edge
                                WHERE points.pid = -pgr.node
                                ORDER BY ST_Distance(points.geom, pgr.next_geom) ASC
                                LIMIT 1)
                        WHEN next_node = -2 THEN  -- End point
                            (SELECT points.geom
                                FROM points
                                -- Get the edge portion that leads to the previous edge
                                WHERE points.pid = -pgr.next_node
                                ORDER BY ST_Distance(points.geom, pgr.prev_geom) ASC
                                LIMIT 1)
                        ELSE
                            edge_geom -- Return the full edge's geometry
                        END AS final_geometry,
                        edge,
                        CASE
                            WHEN node = -1 THEN
                                (SELECT points.fraction_start
                                FROM points
                                WHERE points.pid = -pgr.node
                                ORDER BY points.fraction_start DESC
                                LIMIT 1)
                            ELSE 0
                        END AS fraction_start,
                        CASE
                            WHEN next_node = -2 THEN
                                (SELECT points.fraction_end
                                FROM points
                                WHERE points.pid = -pgr.next_node
                                ORDER BY points.fraction_end ASC
                                LIMIT 1)
                            ELSE 1
                        END AS fraction_end
                    FROM pgr
                )

                SELECT
                    final_geometry as geometry,
                    edge,
                    fraction_start,
                    fraction_end
                FROM route_geometry
                WHERE final_geometry IS NOT NULL
                """

        start_edge = from_step.get('edge_id')
        end_edge = to_step.get('edge_id')
        fraction_start = from_step.get('fraction')
        fraction_end = to_step.get('fraction')

        with connection.cursor() as cursor:
            cursor.execute(query, [
                start_edge, fraction_start,
                start_edge, fraction_start,
                end_edge, fraction_end,
                end_edge, fraction_end,
                start_edge, fraction_start,
                end_edge, fraction_end
            ])

            query_result = cursor.fetchall()
            print(query_result)
            geometries, edge_ids, fraction_starts, fraction_ends = list(zip(*query_result))
            return (
                [
                    MultiLineString(*[GEOSGeometry(geometry)]).merged
                    for geometry in geometries
                ],
                {
                    'positions': dict([
                        (str(i), [fraction_starts[i], fraction_ends[i]])
                        for i in range(len(fraction_starts))
                    ]),
                    'paths': list(edge_ids),
                }
            )

    def create_path_substring(self, path_id, start_fraction, end_fraction):
        path = Path.objects.get(pk=path_id)
        sql = """
        SELECT ST_AsText(ST_SmartLineSubstring('{}'::geometry, {}, {}))
        """.format(path.geom, start_fraction, end_fraction)

        cursor = connection.cursor()
        cursor.execute(sql)
        result = cursor.fetchone()[0]

        # Convert the string into an array of arrays of floats
        coords_str = result.split('(')[1].split(')')[0]
        str_points_array = [elem.split(' ') for elem in coords_str.split(',')]
        arr = [[float(nb) for nb in sub_array] for sub_array in str_points_array]

        line_substring = LineString(arr, srid=settings.SRID)
        return line_substring

    def merge_line_strings(self, line_strings):
        rounded_line_strings = [
            self.round_line_string_coordinates(ls) for ls in line_strings
        ]
        multi_line_string = MultiLineString(rounded_line_strings, srid=settings.SRID)
        return multi_line_string.merged

    # TODO: check if still needed
    def round_line_string_coordinates(self, line_string):
        coords = line_string.coords
        new_coords = [[round(nb, 4) for nb in pt_coord] for pt_coord in coords]
        new_line_string = LineString(new_coords, srid=line_string.srid)
        return new_line_string
