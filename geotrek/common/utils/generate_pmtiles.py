import json
import os
import mercantile
import requests
from mapbox_baselayer.models import MapBaseLayer
from pmtiles.tile import Compression, TileType, zxy_to_tileid
from pmtiles.writer import Writer

from django.conf import settings
from django.contrib.gis.geos import Polygon
from django.utils.translation import gettext_lazy as _

RETRY_COUNT = 3
TMP_PMTILES_PATH = "var/tmp/geotrek_tiles.pmtiles"
PMTILES_PATH = "var/media/pmtiles/geotrek_tiles.pmtiles"
STYLE_PATH = "var/media/pmtiles/geotrek_style.json"


def get_baselayer(pk):
    try:
        return MapBaseLayer.objects.get(pk=pk)
    except MapBaseLayer.DoesNotExist:
        msg = _("MapBaseLayer %(pk)s does not exist") % {"pk": pk}
        raise MapBaseLayer.DoesNotExist(msg)


def get_zooms(min_zoom, max_zoom, baselayer):
    if min_zoom is None and max_zoom is None:
        return list(range(baselayer.min_zoom, baselayer.max_zoom + 1))

    if min_zoom > max_zoom:
        msg = "min_zoom must be smaller than max_zoom"
        raise ValueError(msg)
    if min_zoom < baselayer.min_zoom:
        msg = _("Min zoom must be higher than %(min_zoom)s ") % {
            "min_zoom": baselayer.min_zoom
        }
        raise ValueError(msg)
    if max_zoom > baselayer.max_zoom:
        msg = _("Max zoom must be smaller than %(max_zoom)s ") % {
            "max_zoom": baselayer.max_zoom
        }
        raise ValueError(msg)

    return list(range(min_zoom, max_zoom + 1))


def get_tile_url(baselayer):
    if baselayer.base_layer_type == MapBaseLayer.LayerType.RASTER:
        source = baselayer.get_source()
        return source["tiles"][0], None
    elif baselayer.base_layer_type == MapBaseLayer.LayerType.STYLE_URL:
        url = baselayer.real_url
        response = get_or_retry(url)
        data = response.json()
        return data["sources"]["plan_ign"]["tiles"][
            0
        ], data  # do something more generic for every vector layer


def get_or_retry(url):
    for i in range(RETRY_COUNT):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if i == RETRY_COUNT - 1:
                raise e  # create a custom error


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

    # identify tiles to load
    tiles = list(mercantile.tiles(west, south, east, north, zooms))

    # generate pmtiles
    tile_url, style = get_tile_url(baselayer)
    with open(TMP_PMTILES_PATH, "wb") as f:
        writer = Writer(f)

        for tile in tiles:
            tile_id = zxy_to_tileid(tile.z, tile.x, tile.y)
            url = tile_url.format(z=tile.z, x=tile.x, y=tile.y)
            response = get_or_retry(url)
            tile = response.content

            writer.write_tile(tile_id, tile)

        writer.finalize(
            {
                "tile_type": get_tile_type(baselayer),
                "tile_compression": Compression.NONE,
                "min_zoom": min_zoom,
                "max_zoom": max_zoom + 1,
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

    if style:
        # create json style : remove name and source key
        style.pop("sources")
        style.pop("name")
        with open(STYLE_PATH, "w") as f:
            json.dump(style, f)

    # move pmtiles file into media file
    os.rename(TMP_PMTILES_PATH, PMTILES_PATH)
