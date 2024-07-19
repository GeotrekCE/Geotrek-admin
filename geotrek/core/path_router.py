# import math
# from collections import defaultdict
import json

from django.db import connection
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry, Point, LineString, MultiLineString, GeometryCollection
# from django.core.cache import caches

# import numpy as np
# from scipy.sparse.csgraph import dijkstra
# from scipy.sparse import lil_array

from geotrek.common.utils import sqlfunction
from .models import Path


class PathRouter:
    def __init__(self):
        self.set_path_network_topology()
        # To generate IDs for temporary nodes and edges:
        # self.id_count = 90000000

        # graph = self.graph_edges_nodes_of_qs(Path.objects.exclude(draft=True))
        # self.nodes = graph['nodes']
        # self.edges = graph['edges']
        # self.set_cs_graph()

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

    # def generate_id(self):
    #     new_id = self.id_count
    #     self.id_count += 1
    #     return new_id

    # def get_from_cache_with_latest_paths(self, cache, key):
    #     cached_data = cache.get(key)
    #     latest_paths_date = Path.no_draft_latest_updated()
    #     if cached_data and latest_paths_date:
    #         cache_latest, data = cached_data
    #         if cache_latest and cache_latest >= latest_paths_date:
    #             return latest_paths_date, data
    #     return (latest_paths_date, None)

    # def graph_edges_nodes_of_qs(self, qs):
    #     """
    #     return a graph on the form:
    #     nodes {
    #         coord_point_a {
    #             coord_point_b: edge_id
    #         }
    #     }
    #     edges {
    #         edge_id: {
    #             nodes: [point_a, point_b, ...]
    #             ** extra settings (length etc.)
    #         }
    #     }

    #     coord_poPathRouterint are tuple of float
    #     """

    #     def path_modifier(path):
    #         length = 0.0 if math.isnan(path.length) else path.length
    #         return {"id": path.pk, "length": length}

    #     def get_key_optimizer():
    #         next_id = iter(range(1, 1000000)).__next__
    #         mapping = defaultdict(next_id)
    #         return lambda x: mapping[x]

    #     # Try to retrieve the graph from the cache
    #     cache = caches['fat']
    #     key = 'path_graph'
    #     latest_paths_date, graph = self.get_from_cache_with_latest_paths(cache, key)
    #     if graph is not None:
    #         return graph

    #     key_modifier = get_key_optimizer()
    #     value_modifier = path_modifier

    #     edges = defaultdict(dict)
    #     nodes = defaultdict(dict)

    #     for path in qs:
    #         coords = path.geom.coords
    #         start_point, end_point = coords[0], coords[-1]
    #         k_start_point, k_end_point = key_modifier(start_point), key_modifier(end_point)

    #         v_path = value_modifier(path)
    #         v_path['nodes_id'] = [k_start_point, k_end_point]
    #         edge_id = v_path['id']

    #         nodes[k_start_point][k_end_point] = edge_id
    #         nodes[k_end_point][k_start_point] = edge_id
    #         edges[edge_id] = v_path

    #     graph = {
    #         'edges': dict(edges),
    #         'nodes': dict(nodes),
    #     }
    #     cache.set(key, (latest_paths_date, graph))
    #     return graph

    # def set_cs_graph(self):

    #     # Try to retrieve the matrix from the cache
    #     cache = caches['fat']
    #     key = 'dijkstra_matrix'
    #     latest_paths_date, matrix = self.get_from_cache_with_latest_paths(cache, key)
    #     if matrix is not None:
    #         self.dijk_matrix = matrix
    #         return

    #     nb_of_nodes = len(self.nodes)
    #     nodes_ids = list(self.nodes.keys())
    #     self.dijk_matrix = lil_array((nb_of_nodes, nb_of_nodes), dtype=np.float32)

    #     node_links_list = list(self.nodes.values())
    #     for i, node_links in enumerate(node_links_list):
    #         for (linked_node_id, edge_id) in list(node_links.items()):
    #             # Get the linked node index amongst the still unprocessed nodes:
    #             try:
    #                 col_idx = nodes_ids[i + 1:].index(linked_node_id)
    #             except ValueError:
    #                 col_idx = None
    #             else:
    #                 col_idx += i + 1  # because the index was searched from i+1

    #             # Set the weight of this link
    #             if col_idx is not None:  # else, the weight has already been set
    #                 row_idx = i
    #                 edge_weight = self.get_edge_weight(edge_id)
    #                 self.dijk_matrix[row_idx, col_idx] = edge_weight
    #                 self.dijk_matrix[col_idx, row_idx] = edge_weight

    #     cache.set(key, (latest_paths_date, self.dijk_matrix))

    # def set_edge_weight(self, node1, node2_key, row_idx, col_idx):
    #     """
    #         node1: dict {neighbor_node_key: edge_id, ...}
    #         node2_key: int
    #         row_idx: int
    #         col_idx: int
    #     """
    #     edge_id = node1.get(node2_key)
    #     if edge_id is not None:
    #         # If the nodes are linked by an edge, the weight is its length ;
    #         # if not, the weight stays at 0
    #         edge_weight = self.get_edge_weight(edge_id)
    #         if edge_weight is not None:
    #             self.dijk_matrix[row_idx, col_idx] = edge_weight
    #             self.dijk_matrix[col_idx, row_idx] = edge_weight

    # def get_edge_weight(self, edge_id):
    #     edge = self.edges.get(edge_id)
    #     if edge is None:
    #         return None
    #     return edge.get('length')

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
            line_strings, topology = self.get_two_steps_path(from_step, to_step)
            # all_steps_topologies.append(topology)
            # if line_strings == []:
            #     return [], []
            # one_step_geometry = self.merge_line_strings(line_strings)
            # all_steps_geometries.append(one_step_geometry)
        return all_steps_geometries, all_steps_topologies

    # def compute_two_steps_path_old(self, from_step, to_step):
    #     from_node_info, to_node_info = self.add_steps_to_graph(from_step, to_step)
    #     self.add_steps_to_matrix(from_node_info, to_node_info)

    #     shortest_path = self.get_shortest_path(from_node_info['node_id'],
    #                                            to_node_info['node_id'])
    #     if shortest_path == []:
    #         return [], []
    #     ls, topo = self.get_line_strings_and_topology(shortest_path, from_node_info,
    #                                                   to_node_info)

    #     # Restore the graph (remove the steps)
    #     self.remove_step_from_graph(from_node_info)
    #     self.remove_step_from_graph(to_node_info)
    #     self.remove_steps_from_matrix()

    #     return ls, topo

    def get_two_steps_path(self, from_step, to_step):
        """
        Parameters:
            from_step ({edge_id: int, fraction: float})
            to_step ({edge_id: int, fraction: float})
        """
        if from_step.get('edge_id') == to_step.get('edge_id'):
            # If both points are on same edge, split it from the 1st to the 2nd
            path_substring = self.create_path_substring(
                from_step.get('edge_id'),
                from_step.get('fraction'),
                to_step.get('fraction')
            )
            route_segment = [
                {
                    'geometry': path_substring,
                    'id': from_step.get('edge_id'),
                },
            ]
        else:
            # Compute the shortest path between the two points
            route_segment = self.compute_two_steps_path(from_step, to_step)
        # TODO: also return the serialized topology
        print(route_segment)
        return route_segment, None

    def compute_two_steps_path(self, from_step, to_step):
        query = """
                WITH points as (
                    -- This is a virtual table of the points (start and end)
                    -- and their position on the closest edge
                    SELECT
                        points.pid,
                        points.edge_id,
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
                        (LEAD(pgr.node) OVER (ORDER BY path_seq))
                            AS next_node,
                        (LAG(core_path.geom) OVER (ORDER BY path_seq))
                            AS prev_geom,
                        (LEAD(core_path.geom) OVER (ORDER BY path_seq))
                            AS next_geom
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
                        WHEN node = -2 THEN  -- End point
                            (SELECT points.geom
                                FROM points
                                -- Get the edge portion that leads to the previous edge
                                WHERE points.pid = -pgr.next_node
                                ORDER BY ST_Distance(points.geom, pgr.prev_geom) ASC
                                LIMIT 1)
                        ELSE
                            edge_geom -- Return the full edge's geometry
                        END AS final_geometry,
                        edge
                    FROM pgr
                )

                SELECT
                    final_geometry as geometry,
                    edge
                FROM route_geometry
                WHERE final_geometry IS NOT NULL;
                """

        start_edge = from_step.get('edge_id')
        end_edge = to_step.get('edge_id')
        start_fraction = from_step.get('fraction')
        end_fraction = to_step.get('fraction')

        with connection.cursor() as cursor:
            cursor.execute(query, [
                start_edge, start_fraction,
                start_edge, start_fraction,
                end_edge, end_fraction,
                end_edge, end_fraction,
                start_edge, start_fraction,
                end_edge, end_fraction
            ])
            return [
                {
                    # FIXME
                    'geometry': MultiLineString(*[GEOSGeometry(geometry)]).merged,
                    'id': id
                }
                for geometry, id in cursor.fetchall()
            ]

    # def add_steps_to_graph(self, from_step, to_step):

    #     def create_point_from_coords(lat, lng):
    #         point = Point(lng, lat, srid=settings.API_SRID)
    #         point.transform(settings.SRID)
    #         return point

    #     def fill_point_closest_path_info(point):
    #         # Path and edge info
    #         point['base_path'] = base_path = Path.closest(point['geom'])
    #         point['edge_id'] = edge_id = base_path.pk
    #         point['edge'] = edge = self.edges[edge_id]

    #         # Nodes linked by this edge
    #         point['first_node_id'] = edge.get('nodes_id')[0]
    #         point['last_node_id'] = edge.get('nodes_id')[1]

    #         # Percentage of the Path this point is on
    #         base_path_str = f"'{base_path.geom}'"
    #         point_str = f"'{point['geom'].ewkt}'"
    #         percent_distance = sqlfunction('SELECT ST_LineLocatePoint',
    #                                        base_path_str, point_str)[0]
    #         point['percent_distance'] = percent_distance

    #     # Create a Point corresponding to each step
    #     from_point, to_point = {}, {}
    #     from_point['geom'] = create_point_from_coords(from_step['lat'], from_step['lng'])
    #     to_point['geom'] = create_point_from_coords(to_step['lat'], to_step['lng'])

    #     # Get the Path (and corresponding graph edge info) each Point is on
    #     fill_point_closest_path_info(from_point)
    #     fill_point_closest_path_info(to_point)

    #     # If the steps are on the same edge, it's divided into 3 new edges
    #     if from_point['edge_id'] == to_point['edge_id']:
    #         from_node_info, to_node_info = self.split_edge_in_three(from_point,
    #                                                                 to_point)
    #     # If they are on different edges, both are divided into two new edges
    #     else:
    #         from_node_info = self.split_edge_in_two(from_point)
    #         to_node_info = self.split_edge_in_two(to_point)
    #     return (from_node_info, to_node_info)

    # def remove_step_from_graph(self, node_info):

    #     # Remove the 2 new edges from the graph:
    #     # They will have already been deleted if this is the 2nd step and
    #     # both steps are on the same path
    #     if self.edges.get(node_info['new_edge1_id']) is not None:
    #         del self.edges[node_info['new_edge1_id']]
    #     if self.edges.get(node_info['new_edge2_id']) is not None:
    #         del self.edges[node_info['new_edge2_id']]

    #     # Get the 2 nodes this temporary node is linked to
    #     prev_node = self.nodes.get(node_info['prev_node_id'])
    #     next_node = self.nodes.get(node_info['next_node_id'])

    #     # Remove the new node from the graph
    #     removed_node_id = node_info['node_id']
    #     del self.nodes[removed_node_id]
    #     if prev_node is not None:
    #         # It will have already been deleted if this is the 2nd step and
    #         # both steps are on the same path
    #         del prev_node[removed_node_id]
    #     del next_node[removed_node_id]

    # def split_edge_in_two(self, point_info):

    #     # Get the length of the edges that will be created
    #     path_length = point_info['base_path'].length
    #     dist_to_start = path_length * point_info['percent_distance']
    #     dist_to_end = path_length * (1 - point_info['percent_distance'])

    #     # Create the new node and edges
    #     new_node_id = self.generate_id()
    #     edge1 = {
    #         'id': self.generate_id(),
    #         'length': dist_to_start,
    #         'nodes_id': [point_info['first_node_id'], new_node_id],
    #     }
    #     edge2 = {
    #         'id': self.generate_id(),
    #         'length': dist_to_end,
    #         'nodes_id': [new_node_id, point_info['last_node_id']],
    #     }
    #     first_node, last_node, new_node = {}, {}, {}
    #     first_node[new_node_id] = new_node[point_info['first_node_id']] = edge1['id']
    #     last_node[new_node_id] = new_node[point_info['last_node_id']] = edge2['id']

    #     # Add them to the graph
    #     self.edges[edge1['id']] = edge1
    #     self.edges[edge2['id']] = edge2
    #     self.nodes[new_node_id] = new_node
    #     self.nodes[point_info['first_node_id']].update(first_node)
    #     self.nodes[point_info['last_node_id']].update(last_node)

    #     new_node_info = {
    #         'node_id': new_node_id,
    #         'new_edge1_id': edge1['id'],
    #         'new_edge2_id': edge2['id'],
    #         'prev_node_id': point_info['first_node_id'],
    #         'next_node_id': point_info['last_node_id'],
    #         'original_egde_id': point_info['edge_id'],
    #         'percent_of_edge': point_info['percent_distance'],
    #     }
    #     return new_node_info

    # def split_edge_in_three(self, from_point, to_point):
    #     # Get the length of the edges that will be created
    #     path_length = from_point['base_path'].length
    #     start_percent = from_point['percent_distance']
    #     end_percent = to_point['percent_distance']

    #     # If we're going backwards relative to the Path direction
    #     start_percent, end_percent = end_percent, start_percent

    #     dist_to_start = path_length * start_percent
    #     dist_to_end = path_length * (1 - end_percent)
    #     dist_middle = path_length - dist_to_start - dist_to_end

    #     # Create the new nodes and edges
    #     new_node_id_1 = self.generate_id()
    #     new_node_id_2 = self.generate_id()
    #     edge1 = {
    #         'id': self.generate_id(),
    #         'length': dist_to_start,
    #         'nodes_id': [from_point['first_node_id'], new_node_id_1],
    #     }
    #     edge2 = {
    #         'id': self.generate_id(),
    #         'length': dist_middle,
    #         'nodes_id': [new_node_id_1, new_node_id_2],
    #     }
    #     edge3 = {
    #         'id': self.generate_id(),
    #         'length': dist_to_end,
    #         'nodes_id': [new_node_id_2, from_point['last_node_id']],
    #     }

    #     # Link them together and to the existing nodes
    #     first_node, last_node, new_node_1, new_node_2 = {}, {}, {}, {}
    #     first_node[new_node_id_1] = new_node_1[from_point['first_node_id']] = edge1['id']
    #     new_node_1[new_node_id_2] = new_node_2[new_node_id_1] = edge2['id']
    #     new_node_2[from_point['last_node_id']] = last_node[new_node_id_2] = edge3['id']

    #     # Add them to the graph
    #     self.edges[edge1['id']] = edge1
    #     self.edges[edge2['id']] = edge2
    #     self.edges[edge3['id']] = edge3
    #     self.nodes[new_node_id_1] = new_node_1
    #     self.nodes[new_node_id_2] = new_node_2
    #     self.nodes[from_point['first_node_id']].update(first_node)
    #     self.nodes[from_point['last_node_id']].update(last_node)

    #     new_node_info_1 = {
    #         'node_id': new_node_id_1,
    #         'new_edge1_id': edge1['id'],
    #         'new_edge2_id': edge2['id'],
    #         'prev_node_id': from_point['first_node_id'],
    #         'next_node_id': new_node_id_2,
    #         'original_egde_id': from_point['edge_id'],
    #         'percent_of_edge': from_point['percent_distance'],
    #     }
    #     new_node_info_2 = {
    #         'node_id': new_node_id_2,
    #         'new_edge1_id': edge2['id'],
    #         'prev_node_id': new_node_id_1,
    #         'next_node_id': from_point['last_node_id'],
    #         'new_edge2_id': edge3['id'],
    #         'original_egde_id': from_point['edge_id'],
    #         'percent_of_edge': to_point['percent_distance'],
    #     }
    #     return new_node_info_1, new_node_info_2

    # def add_steps_to_matrix(self, from_node_info, to_node_info):
    #     # Add two rows and two columns
    #     length = self.dijk_matrix.get_shape()[0]
    #     self.dijk_matrix.resize((length + 2, length + 2))

    #     # Add the weights
    #     from_node_key = from_node_info['node_id']
    #     to_node_key = to_node_info['node_id']
    #     for i, node1 in enumerate(list(self.nodes.values())):
    #         for j, node2_key in enumerate([from_node_key, to_node_key]):
    #             row_idx = i
    #             col_idx = length + j
    #             self.set_edge_weight(node1, node2_key, row_idx, col_idx)

    # def remove_steps_from_matrix(self):
    #     length = self.dijk_matrix.get_shape()[0]
    #     self.dijk_matrix.resize((length - 2, length - 2))

    # def get_shortest_path(self, from_node_id, to_node_id):
    #     # List of all nodes IDs -> to interprete dijkstra results
    #     self.nodes_ids = list(self.nodes.keys())

    #     def get_node_idx_per_id(node_id):
    #         try:
    #             return self.nodes_ids.index(node_id)
    #         except ValueError:
    #             return None

    #     def get_node_id_per_idx(node_idx):
    #         if node_idx < 0 or node_idx >= len(self.nodes_ids):
    #             return None
    #         return self.nodes_ids[node_idx]

    #     from_node_idx = get_node_idx_per_id(from_node_id)
    #     to_node_idx = get_node_idx_per_id(to_node_id)
    #     if from_node_idx is None or to_node_idx is None:
    #         return []
    #     result = dijkstra(self.dijk_matrix, return_predecessors=True, indices=from_node_idx,
    #                       directed=False)

    #     # Retrace the path ID by ID, from end to start
    #     predecessors = result[1]
    #     current_node_id, current_node_idx = to_node_id, to_node_idx
    #     path = [current_node_id]
    #     while current_node_id != from_node_id:
    #         if current_node_idx < 0:
    #             # The path ends here but this node is not the destination
    #             return []
    #         current_node_idx = predecessors[current_node_idx]
    #         current_node_id = get_node_id_per_idx(current_node_idx)
    #         path.append(current_node_id)

    #     path.reverse()
    #     return path

    def get_line_strings_and_topology(self, node_list, from_node_info, to_node_info):
        line_strings = []
        topology = {
            'positions': {},
            'paths': [],
        }
        # Get a LineString for each pair of adjacent nodes in the path
        for i in range(len(node_list) - 1):
            # Get the id of the edge corresponding to these nodes
            node1 = self.nodes[node_list[i]]
            node2 = self.nodes[node_list[i + 1]]
            edge_id = self.get_edge_id_by_nodes(node1, node2)

            # Start and end percentages of the line substring
            start_fraction = 0
            end_fraction = 1
            # If this pair of nodes requires to go backwards relative to a
            # Path direction (i.e. the edge 2nd node is the 1st of this pair)
            if self.edges[edge_id]['nodes_id'][1] == node_list[i]:
                start_fraction, end_fraction = end_fraction, start_fraction

            # If it's the first or last edge of this subpath (it can be both!),
            # then the edge is temporary (i.e. created because of a step)
            if i == 0 or i == len(node_list) - 2:
                if i == 0:
                    original_path = Path.objects.get(pk=from_node_info['original_egde_id'])
                    start_fraction = from_node_info['percent_of_edge']
                if i == len(node_list) - 2:
                    original_path = Path.objects.get(pk=to_node_info['original_egde_id'])
                    end_fraction = to_node_info['percent_of_edge']

                line_substring = self.create_line_substring(
                    original_path.geom,
                    start_fraction,
                    end_fraction
                )
                line_strings.append(line_substring)

            # If it's a real edge (i.e. it corresponds to a whole path),
            # we use its LineString
            else:
                original_path = Path.objects.get(pk=edge_id)
                line_strings.append(original_path.geom)

            topology['positions'][i] = [start_fraction, end_fraction]
            topology['paths'].append(original_path.pk)

        return line_strings, topology

    # def get_edge_id_by_nodes(self, node1, node2):
    #     for value in node1.values():
    #         if value in node2.values():
    #             return value
    #     return None

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

    # def create_line_substring(self, geometry, start_fraction, end_fraction):
    #     sql = """
    #     SELECT ST_AsText(ST_SmartLineSubstring('{}'::geometry, {}, {}))
    #     """.format(geometry, start_fraction, end_fraction)

    #     cursor = connection.cursor()
    #     cursor.execute(sql)
    #     result = cursor.fetchone()[0]

    #     # Convert the string into an array of arrays of floats
    #     coords_str = result.split('(')[1].split(')')[0]
    #     str_points_array = [elem.split(' ') for elem in coords_str.split(',')]
    #     arr = [[float(nb) for nb in sub_array] for sub_array in str_points_array]

    #     line_substring = LineString(arr, srid=settings.SRID)
    #     return line_substring

    def merge_line_strings(self, line_strings):
        rounded_line_strings = [
            self.round_line_string_coordinates(ls) for ls in line_strings
        ]
        multi_line_string = MultiLineString(rounded_line_strings, srid=settings.SRID)
        return multi_line_string.merged

    def round_line_string_coordinates(self, line_string):
        coords = line_string.coords
        new_coords = [[round(nb, 4) for nb in pt_coord] for pt_coord in coords]
        new_line_string = LineString(new_coords, srid=line_string.srid)
        return new_line_string
