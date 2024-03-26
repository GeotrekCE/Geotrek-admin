import logging
import re

from django.conf import settings
from landez import TilesManager
from landez.sources import DownloadError


logger = logging.getLogger(__name__)


class ZipTilesBuilder:
    def __init__(self, zipfile, prefix="", **builder_args):
        self.zipfile = zipfile
        self.prefix = prefix
        builder_args['tile_format'] = self.format_from_url(builder_args['tiles_url'])
        self.tm = TilesManager(**builder_args)

        if not isinstance(settings.MOBILE_TILES_URL, str) and len(settings.MOBILE_TILES_URL) > 1:
            for url in settings.MOBILE_TILES_URL[1:]:
                args = builder_args
                args['tiles_url'] = url
                args['tile_format'] = self.format_from_url(args['tiles_url'])
                self.tm.add_layer(TilesManager(**args), opacity=1)

        self.tiles = set()

    def format_from_url(self, url):
        """
        Try to guess the tile mime type from the tiles URL.
        Should work with basic stuff like `http://osm.org/{z}/{x}/{y}.png`
        or funky stuff like WMTS (`http://server/wmts?LAYER=...FORMAT=image/jpeg...)
        """
        m = re.search(r'FORMAT=([a-zA-Z/]+)&', url)
        if m:
            return m.group(1)
        return url.rsplit('.')[-1]

    def add_coverage(self, bbox, zoomlevels):
        self.tiles |= set(self.tm.tileslist(bbox, zoomlevels))

    def run(self):
        for tile in self.tiles:
            name = '{prefix}{0}/{1}/{2}{ext}'.format(
                *tile,
                prefix=self.prefix,
                ext=settings.MOBILE_TILES_EXTENSION or self.tm._tile_extension
            )
            try:
                data = self.tm.tile(tile)
            except DownloadError:
                logger.warning("Failed to download tile %s" % name)
            else:
                self.zipfile.writestr(name, data)
