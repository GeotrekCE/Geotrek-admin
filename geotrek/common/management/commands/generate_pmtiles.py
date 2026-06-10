import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import mercantile
import requests
from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from mapbox_baselayer.models import MapBaseLayer
from pmtiles.tile import Compression, TileType, zxy_to_tileid
from pmtiles.writer import Writer
from tqdm import tqdm

RETRY_COUNT = 3
TMP_PATH = "var/tmp/"
PATH = "var/tiles/pmtiles/"

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create pmtiles of the selected baselayer with parallel downloads"

    def add_arguments(self, parser):
        parser.add_argument("id", type=int, help="Baselayer id in MapBaselayer model")
        parser.add_argument(
            "--minzoom", nargs="?", default=None, type=int, help="Minimum zoom level"
        )
        parser.add_argument(
            "--maxzoom", nargs="?", default=None, type=int, help="Maximum zoom level"
        )

    def get_baselayer(self, pk):
        try:
            return MapBaseLayer.objects.get(pk=pk)
        except MapBaseLayer.DoesNotExist:
            msg = _("MapBaseLayer %(pk)s does not exist") % {"pk": pk}
            raise MapBaseLayer.DoesNotExist(msg)

    def get_zooms(self, min_zoom, max_zoom, baselayer):
        if min_zoom is None or min_zoom < baselayer.min_zoom:
            min_zoom = baselayer.min_zoom
            msg = _("Baselayer min zoom has been selected: %(min_zoom)s") % {
                "min_zoom": baselayer.min_zoom
            }
            self.stdout.write(self.style.WARNING(msg))
            logger.warning(msg)
        if max_zoom is None or max_zoom > baselayer.max_zoom:
            max_zoom = baselayer.max_zoom
            msg = _("Baselayer max zoom has been selected: %(max_zoom)s ") % {
                "max_zoom": baselayer.max_zoom
            }
            self.stdout.write(self.style.WARNING(msg))
            logger.warning(msg)

        return list(range(min_zoom, max_zoom + 1))

    def get_json(self, baselayer):
        if baselayer.base_layer_type == MapBaseLayer.LayerType.RASTER:
            return baselayer.tilejson
        elif baselayer.base_layer_type == MapBaseLayer.LayerType.STYLE_URL:
            url = baselayer.real_url
            response = self.get_or_retry(url)
            return response.json()

    def get_tile_url(self, data):
        source = next(iter(data["sources"].values()))
        return source["tiles"][0]

    def get_or_retry(self, url):
        last_exc = None
        for attempt in range(RETRY_COUNT):
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                last_exc = e
                logger.warning(
                    "Failed attempt %d/%d for %s: %s", attempt + 1, RETRY_COUNT, url, e
                )
                if attempt < RETRY_COUNT - 1:
                    time.sleep(2 ** (attempt + 1))
        msg = f"Failed after {RETRY_COUNT} attempt : {url}"
        raise requests.exceptions.RetryError(msg) from last_exc

    def get_tile_type(self, baselayer):
        if baselayer.base_layer_type == MapBaseLayer.LayerType.RASTER:
            return TileType.PNG
        elif baselayer.base_layer_type == MapBaseLayer.LayerType.STYLE_URL:
            return TileType.MVT

    def download_tile_worker(self, tile_id, url):
        """Worker exécuté en parallèle pour télécharger le contenu brut d'une tuile"""
        try:
            response = self.get_or_retry(url)
            return tile_id, response.content
        except Exception as e:
            logger.error("Impossible de télécharger la tuile %s : %s", url, e)
            return tile_id, None

    def handle(self, *args, **options):
        baselayer_id = options["id"]
        input_minzoom = options["minzoom"]
        input_maxzoom = options["maxzoom"]

        start_time = time.perf_counter()

        # 1. Initialisation et configuration des zooms
        baselayer = self.get_baselayer(baselayer_id)
        zooms = self.get_zooms(input_minzoom, input_maxzoom, baselayer)

        # 2. Projection spatiale de l'emprise
        bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
        bbox.srid = settings.SRID
        bbox.transform(settings.API_SRID)
        west, south, east, north = bbox.extent

        data = self.get_json(baselayer)
        tile_url = self.get_tile_url(data)
        filename_tiles = f"{baselayer.slug}.pmtiles"

        os.makedirs(TMP_PATH, exist_ok=True)
        os.makedirs(PATH, exist_ok=True)

        # 3. Collecte et ordonnancement de toutes les tuiles
        self.stdout.write("Calcul du nombre total de tuiles...")
        all_tiles_to_process = []
        for zoom in zooms:
            tiles_at_zoom = list(mercantile.tiles(west, south, east, north, [zoom]))
            for t in tiles_at_zoom:
                t_id = zxy_to_tileid(t.z, t.x, t.y)
                t_url = tile_url.format(z=t.z, x=t.x, y=t.y)
                all_tiles_to_process.append((t_id, t_url))

        # Important pour PMTiles : Trier par tile_id croissant
        all_tiles_to_process.sort(key=lambda x: x[0])
        total_tiles = len(all_tiles_to_process)
        self.stdout.write(f"Nombre total de tuiles à télécharger : {total_tiles}")

        if total_tiles == 0:
            self.stdout.write("Aucune tuile à générer.")
            return

        # 4. Téléchargement parallèle & Écriture ordonnée
        self.stdout.write("Début de la génération parallélisée...")

        # Structure temporaire pour stocker les tuiles reçues dans le désordre
        downloaded_cache = {}

        with open(f"{TMP_PATH}{filename_tiles}", "wb") as f:
            writer = Writer(f)

            # max_workers=10 pour ne pas saturer le serveur distant tout en restant rapide
            with ThreadPoolExecutor(max_workers=10) as executor:
                with tqdm(
                    total=total_tiles, desc="Progression", unit="tuile", ncols=100
                ) as pbar:
                    # Soumission de tous les téléchargements aux threads
                    future_to_tile = {
                        executor.submit(self.download_tile_worker, t_id, t_url): t_id
                        for t_id, t_url in all_tiles_to_process
                    }

                    # Index de la prochaine tuile attendue pour respecter l'ordre strict de PMTiles
                    next_tile_index = 0

                    for future in as_completed(future_to_tile):
                        t_id, tile_content = future.result()
                        pbar.update(1)

                        if tile_content is not None:
                            # Stockage temporaire en mémoire RAM
                            downloaded_cache[t_id] = tile_content

                        # Écriture immédiate de toutes les tuiles prêtes qui respectent l'ordre croissant
                        while next_tile_index < total_tiles:
                            expected_id, _ = all_tiles_to_process[next_tile_index]

                            if expected_id in downloaded_cache:
                                content = downloaded_cache.pop(expected_id)
                                writer.write_tile(expected_id, content)
                                next_tile_index += 1
                            else:
                                # La prochaine tuile requise dans l'ordre n'est pas encore téléchargée,
                                # on attend que les prochains threads se terminent
                                break

            # 5. Finalisation du fichier PMTiles
            self.stdout.write("Finalisation et indexation du conteneur PMTiles...")
            writer.finalize(
                {
                    "tile_type": self.get_tile_type(baselayer),
                    "tile_compression": Compression.NONE,
                    "min_zoom": zooms[0],
                    "max_zoom": zooms[-1],
                    "min_lon_e7": int(west * 10000000),
                    "min_lat_e7": int(south * 10000000),
                    "max_lon_e7": int(east * 10000000),
                    "max_lat_e7": int(north * 10000000),
                },
                {
                    "attribution": baselayer.attribution,
                    "type": "baselayer",
                },
            )

        # 6. Génération du fichier style JSON (sans la clé sources)
        data.pop("sources", None)
        filename_style = f"{baselayer.slug}.json"
        with open(f"{PATH}{filename_style}", "w") as f:
            json.dump(data, f)

        # Déplacement du fichier final
        os.rename(f"{TMP_PATH}{filename_tiles}", f"{PATH}{filename_tiles}")

        end_time = time.perf_counter()
        self.stdout.write(
            self.style.SUCCESS(
                f"PMTiles et Style générés avec succès en {end_time - start_time:.2f} secondes."
            )
        )
