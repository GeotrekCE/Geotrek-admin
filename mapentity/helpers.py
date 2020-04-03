import itertools
import json
import logging
import math
import os
import string
import time
from datetime import datetime
from mimetypes import types_map

import bs4
import requests
from django.conf import settings
from django.contrib.gis.gdal.error import GDALException
from django.contrib.gis.geos import GEOSException, fromstr
from django.urls import resolve
from django.http import HttpResponse
from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template
from django.utils import six
from django.utils import timezone
from django.utils.six.moves.urllib.parse import urljoin, quote
from django.utils.translation import get_language

from .settings import app_settings, API_SRID

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
    return iter(lambda: map(round, next(gen)), None)


def api_bbox(bbox, srid=None, buffer=0.0):
    """ Receives a tuple(xmin, ymin, xmax, ymax) and
    returns a tuple in API projection.

    :srid: bbox projection (Default: settings.SRID)
    :buffer: grow the bbox in ratio of width (Default: 0.0)
    """
    srid = srid or settings.SRID
    wkt_box = 'POLYGON(({0} {1}, {2} {1}, {2} {3}, {0} {3}, {0} {1}))'
    wkt = wkt_box.format(*bbox)
    native = wkt_to_geom(wkt, srid_from=srid)
    if srid != API_SRID:
        native.transform(API_SRID)
    if buffer > 0:
        extent = native.extent
        width = extent[2] - extent[0]
        native = native.buffer(width * buffer)
    return tuple(native.extent)


def wkt_to_geom(wkt, srid_from=None, silent=False):
    if srid_from is None:
        srid_from = API_SRID
    try:
        return fromstr(wkt, srid=srid_from)
    except (GDALException, GEOSException) as e:
        if not silent:
            raise e
        return None


def transform_wkt(wkt, srid_from=None, srid_to=None, dim=3):
    """
    Changes SRID, and returns 3D wkt
    """
    if srid_from is None:
        srid_from = API_SRID
    if srid_to is None:
        srid_to = settings.SRID
    try:
        geom = fromstr(wkt, srid=srid_from)
        if srid_from != srid_to:
            geom.transform(srid_to)
        extracoords = ' 0.0' * (dim - 2)  # add missing dimensions
        wkt3d = geom.wkt.replace(',', extracoords + ',')
        wkt3d = wkt3d.replace(')', extracoords + ')')
        return 'SRID=%s;%s' % (srid_to, wkt3d)
    except (GDALException, GEOSException, TypeError, ValueError) as e:
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

    if date_update is None:
        return False

    if os.path.getsize(path) == 0:
        if delete_empty:
            os.remove(path)
        return False

    modified = datetime.utcfromtimestamp(os.path.getmtime(path))
    modified = modified.replace(tzinfo=timezone.utc)
    return modified > date_update


def get_source(url, headers):
    logger.info("Request to: %s" % url)
    source = requests.get(url, headers=headers)

    status_error = 'Request on %s failed (status=%s)' % (url, source.status_code)
    assert source.status_code == 200, status_error

    content_error = 'Request on %s returned empty content' % url
    assert len(source.content) > 0, content_error

    return source


def download_to_stream(url, stream, silent=False, headers=None):
    """ Download url and writes response to stream.
    """
    source = None

    try:
        try:
            source = get_source(url, headers)
        except requests.exceptions.ConnectionError:
            time.sleep(1)
            source = get_source(url, headers)
    except (AssertionError, requests.exceptions.RequestException) as e:
        logger.exception(e)
        logger.info('Headers sent: %s' % headers)
        if hasattr(source, 'text'):
            logger.info('Response: %s' % source.text[:150])

        if not silent:
            raise

    if source is None:
        return source

    try:
        stream.write(source.content)
        stream.flush()
    except IOError as e:
        logger.exception(e)
        if not silent:
            raise

    if isinstance(stream, HttpResponse):
        stream.status_code = source.status_code
        # Copy headers
        for header, value in source.headers.items():
            stream[header] = value

    return source


def convertit_url(url, from_type=None, to_type=None, proxy=False):
    if not to_type:
        to_type = 'application/pdf'
    mimetype = to_type
    if '/' not in mimetype:
        extension = '.' + mimetype if not mimetype.startswith('.') else mimetype
        mimetype = types_map[extension]

    fromparam = ("&from=%s" % quote(from_type)) if from_type is not None else ''
    params = 'url={url}{fromparam}&to={to}'.format(url=quote(url),
                                                   fromparam=fromparam,
                                                   to=quote(mimetype))
    url = '{server}/?{params}'.format(server=app_settings['CONVERSION_SERVER'],
                                      params=params)
    return url


def convertit_download(url, destination, from_type=None, to_type='application/pdf', headers=None):
    # Mock for tests
    if getattr(settings, 'TEST', False):
        open(destination, 'w').write("Mock\n")
        return

    url = convertit_url(url, from_type, to_type)
    fd = open(destination, 'wb') if isinstance(destination, six.string_types) else destination
    download_to_stream(url, fd, headers=headers)


def capture_url(url, width=None, height=None, selector=None, waitfor=None):
    """Return URL to request a capture from Screamshotter
    """
    server = app_settings['CAPTURE_SERVER']
    width = ('&width=%s' % width) if width else ''
    height = ('&height=%s' % height) if height else ''
    selector = ('&selector=%s' % quote(selector)) if selector else ''
    waitfor = ('&waitfor=%s' % quote(waitfor)) if waitfor else ''
    params = '{width}{height}{selector}{waitfor}'.format(width=width,
                                                         height=height,
                                                         selector=selector,
                                                         waitfor=waitfor)
    capture_url = '{server}/?url={url}{params}'.format(server=server,
                                                       url=quote(url),
                                                       params=params)
    return capture_url


def capture_image(url, stream, **kwargs):
    """Capture url to stream.
    """
    url = capture_url(url, **kwargs)
    download_to_stream(url, stream)


def capture_map_image(url, destination, size=None, aspect=1.0, waitfor='.leaflet-tile-loaded', printcontext=None):
    """Prepare aspect of the detail page

    It relies on JS code in MapEntity.Context
    """
    # Control aspect of captured images
    if size is None:
        size = app_settings['MAP_CAPTURE_SIZE']
    if aspect < 1.0:
        mapsize = dict(width=size * aspect, height=size)
    else:
        mapsize = dict(width=size, height=size / aspect)
    _printcontext = dict(mapsize=mapsize)
    _printcontext['print'] = True
    if printcontext:
        _printcontext.update(printcontext)
    serialized = json.dumps(_printcontext)
    # Run head-less capture (takes time)
    url += '?lang={}&context={}'.format(get_language(), quote(serialized))

    with open(destination, 'wb') as fd:
        capture_image(url, fd,
                      selector='.map-panel',
                      waitfor=waitfor)


def extract_attributes_html(url, request):
    """
    The tidy XHTML version of objects attributes.

    Since we have to insert them in document exports, we extract the
    ``details-panel`` of the detail page, using BeautifulSoup.
    With this, we save a lot of efforts, since we do have to build specific Appy.pod
    templates for each model.
    """
    func, args, kwargs = resolve(url)
    response = func(request, *args, **kwargs)
    response.render()

    soup = bs4.BeautifulSoup(response.content, 'lxml')
    details = soup.find(id="properties")
    if details is None:
        raise ValueError('Content is of detail page is invalid')

    # Remove "Add" buttons
    for p in details('p'):
        if 'autohide' in p.get('class', ''):
            p.extract()
    # Remove Javascript
    for s in details('script'):
        s.extract()
    # Remove images (Appy.pod fails with them)
    for i in details('img'):
        i.replaceWith(i.get('title', ''))
    # Remove links (Appy.pod sometimes shows empty strings)
    for a in details('a'):
        a.replaceWith(a.text)
    # Prettify (ODT compat.) and convert unicode to XML entities
    cooked = details.prettify('ascii', formatter='html').decode()
    return cooked


def user_has_perm(user, perm):
    # First check if the user has the permission (even anon user)
    if user.has_perm(perm):
        return True
    if user.is_anonymous:
        return perm in app_settings['ANONYMOUS_VIEWS_PERMS']
    return False


def alphabet_enumeration(length):
    """
    Return list of letters : A, B, ... Z, AA, AB, ...
    See mapentity/leaflet.enumeration.js
    """
    if length == 0:
        return []
    if length == 1:
        return ["A"]
    width = int(math.ceil(math.log(length, 26)))
    enums = []
    alphabet = string.ascii_uppercase
    for i in range(length):
        enum = ""
        for j in range(width):
            enum = alphabet[i % 26] + enum
            i = i // 26
        enums.append(enum)
    return enums


def suffix_for(template_name_suffix, template_type, extension):
    return "%s%s.%s" % (template_name_suffix, template_type, extension)


def name_for(app, modelname, suffix):
    return "%s/%s%s" % (app, modelname, suffix)


def smart_get_template(model, suffix):
    for appname, modelname in [(model._meta.app_label, model._meta.object_name.lower()),
                               ("mapentity", "override"),
                               ("mapentity", "mapentity")]:
        try:
            template_name = name_for(appname, modelname, suffix)
            get_template(template_name)  # Will raise if not exist
            return template_name
        except TemplateDoesNotExist:
            pass
    return None
