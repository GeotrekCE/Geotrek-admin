from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from leuvenmapmatching.matcher.distance import DistanceMatcher
from leuvenmapmatching.map.inmem import InMemMap
from leuvenmapmatching import visualization as mmviz
from leuvenmapmatching.util.gpx import gpx_to_path


class Command(BaseCommand):
  help = "Run Leuven Map Matching with core_path network using a GPX file."

  def add_arguments(self, parser):
    parser.add_argument(
        "gpx_file", type=str, help="Path to the GPX file to match"
    )
    parser.add_argument(
        "--output", default="zmm/mapmatching.png", help="Filename for the output visualization image (default: mapmatching.png)",
    )
    parser.add_argument(
        "--max-dist", type=float, default=50, help="Max distance for matching in meters (default: 50)",
    )
    parser.add_argument(
        "--obs-noise", type=float, default=50, help="Noise for matching in meters (default: 10)",
    )
    parser.add_argument(
        "--create", action="create_true", help="Add if you want to create Topology and Pathaggregation (default: False)"
    )

  def handle(self, *args, **options):
    gpx_path = options["gpx_file"]
    output_filename = options["output"]
    max_dist = options["max_dist"]
    obs_noise = options["obs_noise"]

    track_gpx = Path(gpx_path)

    with connection.cursor() as cursor:
      cursor.execute(
          "SELECT id, ST_AsText(ST_Transform(geom, 4326)) FROM core_path;"
      )
      rows = cursor.fetchall()

    coord_to_node_id = {}
    graph = {}
    node_counter = 0

    for tronc_id, geom in rows:

      coords_content = geom.replace("LINESTRING(", "").replace(")", "")
      points = coords_content.split(",")

      seg_node_ids = []
      for p in points:
        parts = p.strip().split()
        lon = float(parts[0]) 
        lat = float(parts[1])
        coord = (lat, lon) 

        if coord not in coord_to_node_id:
          coord_to_node_id[coord] = node_counter
          graph[node_counter] = (coord, [])
          node_counter += 1
        seg_node_ids.append(coord_to_node_id[coord])

      for i in range(len(seg_node_ids) - 1):
        a, b = seg_node_ids[i], seg_node_ids[i + 1]
        if b not in graph[a][1]:
          graph[a][1].append(b)
        if a not in graph[b][1]:
          graph[b][1].append(a)

    mapdb = InMemMap(
        "geotrek_map",
        graph=graph,
        use_latlon=True,
        use_rtree=True,
        index_edges=True)

    track = gpx_to_path(track_gpx)

    matcher = DistanceMatcher(
        mapdb,
        max_dist=max_dist,
        max_dist_init=max_dist,
        obs_noise=obs_noise,
        obs_noise_ne=obs_noise,
        dist_noise=50,
        non_emitting_states=False,
        only_edges=False,
    )

    states, lastidx = matcher.match(track)
    nodes = matcher.path_pred_onlynodes

    mmviz.plot_map(
        mapdb,
        matcher=matcher,
        use_osm=True,
        zoom_path=True,
        show_graph=True,
        show_labels=False,
        show_matching=True,
        filename=output_filename,
    )