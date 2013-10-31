from collections import defaultdict


def graph_edges_nodes_of_qs(qs, key_modifier=lambda x: x, value_modifier=lambda x: x):
    """
    return a graph on the form:
    nodes {
        coord_point_a {
            coord_point_b: edge_id
        }
    }
    edges {
        edge_id: {
            nodes: [point_a, point_b, ...]
            ** extra settings (length etc.)
        }
    }


    coord_point are tuple of float
    """

    edges = defaultdict(dict)
    nodes = defaultdict(dict)

    for path in qs:
        coords = path.geom.coords
        start_point, end_point = coords[0], coords[-1]
        k_start_point, k_end_point = key_modifier(start_point), key_modifier(end_point)

        # must return a dict with a id
        v_path = value_modifier(path)
        v_path['nodes_id'] = [k_start_point, k_end_point]
        edge_id = v_path['id']

        nodes[k_start_point][k_end_point] = edge_id
        nodes[k_end_point][k_start_point] = edge_id
        edges[edge_id] = v_path

    return {
        'edges': dict(edges),
        'nodes': dict(nodes),
    }
