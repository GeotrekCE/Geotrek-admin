import json
import logging
import time
import os

import mercantile
import requests
from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.utils.translation import gettext_lazy as _
from mapbox_baselayer.models import MapBaseLayer
from pmtiles.tile import Compression, TileType, zxy_to_tileid
from pmtiles.writer import Writer

RETRY_COUNT = 3
TMP_PATH = "var/tmp/"
PATH = "var/tiles/pmtiles/"

logger = logging.getLogger(__name__)


def get_baselayer(pk):
    try:
        return MapBaseLayer.objects.get(pk=pk)
    except MapBaseLayer.DoesNotExist:
        msg = _("MapBaseLayer %(pk)s does not exist") % {"pk": pk}
        raise MapBaseLayer.DoesNotExist(msg)


def get_zooms(min_zoom, max_zoom, baselayer):
    if min_zoom is None or min_zoom < baselayer.min_zoom:
        min_zoom = baselayer.min_zoom
        msg = _("Baselayer min zoom has been selected: %(min_zoom)s") % {
            "min_zoom": baselayer.min_zoom
        }
        logger.warning(msg)
    if max_zoom is None or max_zoom > baselayer.max_zoom:
        max_zoom = baselayer.max_zoom
        msg = _("Baselayer max zoom has been selected: %(max_zoom)s ") % {
            "max_zoom": baselayer.max_zoom
        }
        logger.warning(msg)

    return list(range(min_zoom, max_zoom + 1))


def get_json(baselayer):
    if baselayer.base_layer_type == MapBaseLayer.LayerType.RASTER:
        return baselayer.tilejson
    elif baselayer.base_layer_type == MapBaseLayer.LayerType.STYLE_URL:
        url = baselayer.real_url
        response = get_or_retry(url)
        data = response.json()
        return data


def get_tile_url(data):
    source = next(iter(data["sources"].values()))
    return source["tiles"][0]


def get_or_retry(url):
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
                time.sleep(2 ** (attempt+1))

    raise requests.exceptions.RetryError(
        f"Failed after {RETRY_COUNT} attempt : {url}"
    ) from last_exc


def get_tile_type(baselayer):
    if baselayer.base_layer_type == MapBaseLayer.LayerType.RASTER:
        return TileType.PNG
    elif baselayer.base_layer_type == MapBaseLayer.LayerType.STYLE_URL:
        return TileType.MVT  # Maplibre Vector Tile


def generate_pmtiles(baselayer_id, min_zoom=None, max_zoom=None):
    # get MapBaseLayer
    baselayer = get_baselayer(baselayer_id)
    zooms = get_zooms(min_zoom, max_zoom, baselayer)

    # convert SPATIAL_EXTENT projection to 4326
    bbox = Polygon.from_bbox(settings.SPATIAL_EXTENT)
    bbox.srid = settings.SRID
    bbox.transform(settings.API_SRID)
    west, south, east, north = bbox.extent

    data = get_json(baselayer)
    tile_url = get_tile_url(data)
    filename_tiles = f"{baselayer.slug}.pmtiles"

    os.makedirs(TMP_PATH, exist_ok=True)
    os.makedirs(PATH, exist_ok=True)

    with open(f"{TMP_PATH}{filename_tiles}", "wb") as f:
        writer = Writer(f)
        # compute the tiles for each zoom level separately to avoid overusing memory.
        for zoom in zooms:
            stats = 0
            # identify tiles to load
            tiles = list(mercantile.tiles(west, south, east, north, [zoom]))
            logger.info("Zoom %d : %d tiles to download", zoom, len(tiles))

            # generate pmtiles
            for tile in tiles:
                tile_id = zxy_to_tileid(tile.z, tile.x, tile.y)
                url = tile_url.format(z=tile.z, x=tile.x, y=tile.y)
                response = get_or_retry(url)
                tile = response.content

                writer.write_tile(tile_id, tile)
                stats += 1
                logger.info("Zoom %d : %d/%d", zoom, stats, len(tiles))

        writer.finalize(
            {
                "tile_type": get_tile_type(baselayer),
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

    # create json style : remove source key
    data.pop("sources")
    filename_style = f"{baselayer.slug}.json"

    with open(f"{PATH}{filename_style}", "w") as f:
        json.dump(data, f)

    # move pmtiles file into media file
    os.rename(f"{TMP_PATH}{filename_tiles}", f"{PATH}{filename_tiles}")
