from pathlib import Path

from django.contrib.gis.db.models.functions import Transform
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from leuvenmapmatching.matcher.distance import DistanceMatcher
from leuvenmapmatching.map.inmem import InMemMap
from leuvenmapmatching import visualization as mmviz
from leuvenmapmatching.util.gpx import gpx_to_path

from geotrek.core.models import Path as CorePath
from geotrek.core.models import Trail
from geotrek.authent.models import Structure


class Command(BaseCommand):
    help = "Run Leuven Map Matching with core_path network using a GPX file."

    def add_arguments(self, parser):
        parser.add_argument("gpx_file", type=str, help="Path to the GPX file to match")
        parser.add_argument(
            "--output", default="zmm/mapmatching.png",
            help="Filename for the output visualization image (default: mapmatching.png)",
        )
        parser.add_argument("--max-dist", type=float, default=50,
                             help="Max distance for matching in meters (default: 50)")
        parser.add_argument("--obs-noise", type=float, default=50,
                             help="Noise for matching in meters (default: 10)")
        parser.add_argument("--insert", action="store_true",
                             help="Créer une Topology + PathAggregations en base à partir du matching")
        parser.add_argument("--kind", default="TOPOLOGY",
                             help="Kind de la Topology créée si --insert (défaut: TOPOLOGY)")
        parser.add_argument( "--name", default="Trail", 
                            help="Tral name")
        parser.add_argument("--structure", type=int, default=1,
                            help="Structure name")

    def handle(self, *args, **options):
        gpx_path = options["gpx_file"]
        output_filename = options["output"]
        max_dist = options["max_dist"]
        obs_noise = options["obs_noise"]
        track_gpx = Path(gpx_path)

        if not track_gpx.exists():
            raise CommandError(f"GPX file not found: {track_gpx}")

        mapdb, edge_meta = self.build_map()

        track = gpx_to_path(track_gpx)

        matcher = DistanceMatcher(
            mapdb,
            max_dist=max_dist,
            max_dist_init=max_dist,
            obs_noise=obs_noise,
            obs_noise_ne=obs_noise,
            dist_noise=50,
            non_emitting_states=True,  
            only_edges=True,           
        )

        states, lastidx = matcher.match(track)
        nodes = matcher.path_pred_onlynodes

        aggregations = self.build_aggregations(nodes, edge_meta)
        self.stdout.write("Aggregations reconstruites:")
        for agg in aggregations:
            self.stdout.write(f"  {agg}")

        if options["insert"]:
            if not aggregations:
                raise CommandError("Aucune aggregation reconstruite, rien à insérer.")
            if not options["structure"]:
                raise CommandError("--structure est obligatoire avec --insert (id de Structure).")
            structure = Structure.objects.get(pk=options["structure"])
            trail = self.insert_trail(aggregations, name=options["name"], structure=structure)
            self.stdout.write(self.style.SUCCESS(f"Trail créé: id={trail.pk}, name={trail.name}"))

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

    def build_map(self):
        coord_to_node_id = {}
        graph = {}
        node_counter = 0
        edge_meta = {}

        paths_qs = CorePath.objects.all().only("id", "geom")

        for path_obj in paths_qs:
            geom_native = path_obj.geom 
            geom_ll = geom_native.transform(4326, clone=True)

            coords_native = list(geom_native.coords)
            coords_ll = [(lat, lon) for lon, lat in geom_ll.coords]

            cum = [0.0]
            for i in range(len(coords_native) - 1):
                x1, y1 = coords_native[i]
                x2, y2 = coords_native[i + 1]
                cum.append(cum[-1] + ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5)
            total_length = cum[-1] or 1.0

            seg_node_ids = []
            for coord in coords_ll:
                if coord not in coord_to_node_id:
                    coord_to_node_id[coord] = node_counter
                    graph[node_counter] = (coord, [])
                    node_counter += 1
                seg_node_ids.append(coord_to_node_id[coord])

            for i in range(len(seg_node_ids) - 1):
                a, b = seg_node_ids[i], seg_node_ids[i + 1]
                start_pos = cum[i] / total_length
                end_pos = cum[i + 1] / total_length

                if b not in graph[a][1]:
                    graph[a][1].append(b)
                if a not in graph[b][1]:
                    graph[b][1].append(a)

                edge_meta[(a, b)] = {"path_id": path_obj.pk, "start_position": start_pos, "end_position": end_pos}
                edge_meta[(b, a)] = {"path_id": path_obj.pk, "start_position": end_pos, "end_position": start_pos}



        mapdb = InMemMap("geotrek_map", graph=graph, use_latlon=True, use_rtree=True, index_edges=True)

        return mapdb, edge_meta

    def build_aggregations(self, nodes, edge_meta):
        raw_segments = []
        for i in range(len(nodes) - 1):
            a, b = nodes[i], nodes[i + 1]
            meta = edge_meta.get((a, b))
            if meta is None:
                self.stderr.write(self.style.WARNING(f"pas d'arête directe entre {a} et {b}"))
                continue
            raw_segments.append(meta)

        aggregations = []
        for seg in raw_segments:
            if aggregations and aggregations[-1]["path_id"] == seg["path_id"]:
                aggregations[-1]["end_position"] = seg["end_position"]
            else:
                aggregations.append({
                    "path_id": seg["path_id"],
                    "start_position": seg["start_position"],
                    "end_position": seg["end_position"],
                })

        for idx, agg in enumerate(aggregations):
            agg["order"] = idx

        return aggregations

    
    @transaction.atomic
    def insert_trail(self, aggregations, name, structure):
        trail = Trail.objects.create(name=name, structure=structure)
        path_cache = {}
        for agg in aggregations:
            path_id = agg["path_id"]
            if path_id not in path_cache:
                path_cache[path_id] = CorePath.objects.get(pk=path_id)
            trail.add_path(
                path_cache[path_id],
                start=agg["start_position"],
                end=agg["end_position"],
                order=agg["order"],
                reload=False,
            )
        trail.reload()
        return trail