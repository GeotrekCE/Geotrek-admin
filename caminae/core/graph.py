from collections import defaultdict
from .models import Path


def graph_of_qs(qs, key_modifier=lambda x: x, value_modifier=lambda x: x):
    """
    return a graph on the form:
    coord_point_a {
        coord_point_b {
            Path model instance
        }
    }

    coord_point are tuple of float
    """

    graph = defaultdict(dict)
    for path in qs:
        coords = path.geom.coords
        start_point, end_point = coords[0], coords[-1]
        k_start_point, k_end_point = key_modifier(start_point), key_modifier(end_point)

        v_path = value_modifier(path)
        graph[k_start_point][k_end_point] = v_path
        graph[k_end_point][k_start_point] = v_path

    return dict(graph)


json_key_point_modifier = lambda x: '%s_%s' % (x[0], x[1])

def get_key_optimizer():
    next_id = iter(xrange(1, 1000000)).next
    mapping = defaultdict(next_id)

    return lambda x: mapping[x]


def graph_of_qs_string_keys(qs, **kwargs):
    return graph_of_qs(qs, json_key_point_modifier, **kwargs)

def graph_of_qs_optimize(qs, **kwargs):
    key_optimizer = get_key_optimizer()
    return graph_of_qs(qs, key_optimizer, **kwargs)


def optimize_graph(orig_graph):
    get_mapping = get_key_optimizer()

    graph = {}
    for p1, v in orig_graph.iteritems():
        g = graph[get_mapping(p1)] = {}
        for p2, path in v.iteritems():
            g[get_mapping(p2)] = path

    return graph

