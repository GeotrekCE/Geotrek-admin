import os
import urllib2
from urlparse import urljoin
import itertools
import logging
import urllib
from mimetypes import types_map
from datetime import datetime
import json

from django.utils import timezone
from django.conf import settings
from django.contrib.gis.gdal.error import OGRException
from django.contrib.gis.geos import GEOSException, fromstr

import requests
from screamshot.utils import casperjs_capture, CaptureError

from . import app_settings

logger = logging.getLogger(__name__)


def bbox_split(bbox, by_x=2, by_y=2, cycle=False):
    """Divide a box in rectangle, by_x parts and by_y parts"""
    minx, miny, maxx, maxy = bbox

    stepx = (maxx - minx) / by_x
    stepy = (maxy - miny) / by_y

    def gen():
        """define as inner function to decorate it with cycle"""
        stepx_tmp = minx
        while stepx_tmp + stepx <= maxx:
            stepx_next = stepx_tmp + stepx

            stepy_tmp = miny
            while stepy_tmp + stepy <= maxy:
                stepy_next = stepy_tmp + stepy
                yield (stepx_tmp, stepy_tmp, stepx_next, stepy_next)

                stepy_tmp = stepy_next

            stepx_tmp = stepx_next

    if cycle:
        return itertools.cycle(gen())
    else:
        return gen()


def bbox_split_srid_2154(*args, **kwargs):
    """Just round"""
    gen = bbox_split(*args, **kwargs)
    return iter(lambda: map(round, gen.next()), None)


def wkt_to_geom(wkt, srid_from=None, silent=False):
    if srid_from is None:
        srid_from = settings.API_SRID
    try:
        return fromstr(wkt, srid=srid_from)
    except (OGRException, GEOSException) as e:
        if not silent:
            raise e
        return None


def transform_wkt(wkt, srid_from=None, srid_to=None, dim=3):
    """
    Changes SRID, and returns 3D wkt
    """
    if srid_from is None:
        srid_from = settings.API_SRID
    if srid_to is None:
        srid_to = settings.SRID
    try:
        geom = fromstr(wkt, srid=srid_from)
        if srid_from != srid_to:
            geom.transform(srid_to)
        extracoords = ' 0.0' * (dim - 2)  # add missing dimensions
        wkt3d = geom.wkt.replace(',', extracoords + ',')
        wkt3d = wkt3d.replace(')', extracoords + ')')
        return wkt3d
    except (OGRException, GEOSException, TypeError, ValueError), e:
        if settings.DEBUG or not getattr(settings, 'TEST', False):
            logger.error("wkt_to_geom('%s', %s, %s) : %s" % (wkt, srid_from, srid_to, e))
        return None


def smart_urljoin(base, path):
    if base[-1] != '/':
        base += '/'
    if path[0] == '/':
        path = path[1:]
    return urljoin(base, path)


def is_file_newer(path, date_update, delete_empty=True):
    if not os.path.exists(path):
        return False

    if os.path.getsize(path) == 0:
        if delete_empty:
            os.remove(path)
        return False

    modified = datetime.fromtimestamp(os.path.getmtime(path))
    modified = modified.replace(tzinfo=timezone.utc)
    return modified > date_update


def convertit_url(request, sourceurl, from_type=None, to_type='application/pdf'):
    mimetype = to_type
    if '/' not in mimetype:
        extension = '.' + mimetype if not mimetype.startswith('.') else mimetype
        mimetype = types_map[extension]

    fullurl = request.build_absolute_uri(sourceurl)
    fromparam = "&from=%s" % urllib.quote(from_type) if from_type is not None else ''
    url = "%s?url=%s%s&to=%s" % (app_settings['CONVERSION_SERVER'],
                                 urllib.quote(fullurl),
                                 fromparam,
                                 urllib.quote(mimetype))
    if not url.startswith('http'):
        url = '%s://%s%s' % (request.is_secure() and 'https' or 'http',
                             request.get_host(),
                             url)
    return url


def convertit_download(request, source, destination, from_type=None, to_type='pdf'):
    # Mock for tests
    if getattr(settings, 'TEST', False):
        open(destination, 'wb').write("Mock\n")
        return

    url = convertit_url(request, source, from_type, to_type)
    try:
        logger.info("Request to Convertit server: %s" % url)
        source = requests.get(url)
        assert source.status_code == 200, 'Conversion failed (status=%s)' % source.status_code
    except (AssertionError, requests.exceptions.RequestException) as e:
        logger.exception(e)
        if hasattr(source, 'content'):
            logger.error(source.content[:150])
        raise
    # Write locally
    try:
        fd = open(destination, 'wb') if isinstance(destination, basestring) else destination
        fd.write(source.content)
    except IOError as e:
        logger.exception(e)
        raise


def capture_map_image(url, destination, size=None):
    """Prepare aspect of the detail page

    It relies on JS code in MapEntity.Context
    """
    from .models import MapImageError

    if size is None:
        size = app_settings['MAP_CAPTURE_SIZE']
    printcontext = dict(mapsize=size)
    printcontext['print'] = True
    serialized = json.dumps(printcontext)
    try:
        # Run head-less capture (takes time)
        url += '?context=' + urllib2.quote(serialized)
        with open(destination, 'wb') as f:
            casperjs_capture(f, url, selector='.map-panel')  # see templates/entity_detail.html
    except CaptureError as e:
        raise MapImageError(e)

    # If image is empty or missing, raise error
    if not os.path.exists(destination):
        raise MapImageError("No image captured from %s into %s" % (url, destination))
    elif os.path.getsize(destination) == 0:
        os.remove(destination)
        raise MapImageError("Image captured from %s into %s is empty" % (url, destination))
