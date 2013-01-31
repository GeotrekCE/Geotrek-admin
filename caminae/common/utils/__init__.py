import math
import mimetypes
from urlparse import urljoin
import logging

from django.db import connection
from django.conf import settings
from django.utils.timezone import utc
from django.contrib.gis.gdal.error import OGRException
from django.contrib.gis.geos import GEOSException, fromstr, LineString, Point

logger = logging.getLogger(__name__)


class classproperty(object):
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


def dbnow():
    cursor = connection.cursor()
    cursor.execute("SELECT statement_timestamp() AT TIME ZONE 'UTC';")
    row = cursor.fetchone()
    return row[0].replace(tzinfo=utc)


def distance3D(a, b):
    """
    Utility function computing distance between 2 points in 3D-space.
    Will work with coordinates tuples instead of full-fledged geometries,
    that's why is is more convenient than GEOS functions.
    """
    return math.sqrt((b[0] - a[0]) ** 2 +
                     (b[1] - a[1]) ** 2 +
                     (b[2] - a[2]) ** 2)


def elevation_profile(g, maxitems=None):
    """
    Extract elevation profile from a 3D geometry.
    - maxitems : maximum number of points
    """
    if g.geom_type == 'MultiLineString':
        profile = []
        for subcoords in g.coords:
            profile.extend(elevation_profile(LineString(subcoords), maxitems=maxitems))
        return profile

    step = 1
    if maxitems is not None:
        nb = len(g.coords)
        step = max(1, nb / maxitems)
    # Initialize with null distance at start point
    distance = 0.0
    profile = [(distance, g.coords[0][2])]
    # Add elevation and cumulative distance at each point
    for i in range(1, len(g.coords), step):
        a = g.coords[i - step]
        b = g.coords[i]
        distance += distance3D(a, b)
        profile.append((distance, b[2],))
    return profile


def force3D(geom):
    if not geom or geom.geom_type != 'Point':
        raise ValueError('Cannot force 3D on %s' % geom)
    if geom.z != 0:
        return geom
    return Point(geom.x, geom.y, 0)


def wkt_to_geom(wkt, srid_from=None, silent=False):
    if srid_from is None:
        srid_from = settings.API_SRID
    try:
        return fromstr(wkt, srid=srid_from)
    except (OGRException, GEOSException) as e:
        if not silent:
            raise e
        return None

def transform_wkt(wkt, srid_from=None, srid_to=None):
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
        dim = 3
        extracoords = ' 0.0' * (dim - 2)  # add missing dimensions
        wkt3d = geom.wkt.replace(',', extracoords + ',')
        return wkt3d
    except (OGRException, GEOSException, TypeError, ValueError), e:
        if not settings.TEST:
            logger.error("wkt_to_geom('%s', %s, %s) : %s" % (wkt, srid_from, srid_to, e))
        return None

def sqlfunction(function, *args):
    """
    Executes the SQL function with the specified args, and returns the result.
    """
    sql = '%s(%s)' % (function, ','.join(args))
    logger.debug(sql)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 1:
        return result[0]
    return result


def almostequal(v1, v2, precision=2):
    return abs(v1 - v2) < 10**-precision


def smart_urljoin(base, path):
    if base[-1] != '/':
        base += '/'
    if path[0] == '/':
        path = path[1:]
    return urljoin(base, path)


def split_bygeom(iterable, geom_getter=lambda x: x.geom):
    """Split an iterable in two list (points, linestring)"""
    points, linestrings = [], []
    
    for x in iterable:
        geom = geom_getter(x)
        if geom is None:
            pass
        elif isinstance(geom, Point):
            points.append(x)
        elif isinstance(geom, LineString):
            linestrings.append(x)
        else:
            raise ValueError("Only LineString and Point geom should be here. Got %s for pk %d" % (geom, x.pk))
    return points, linestrings


def serialize_imagefield(imagefield):
    try:
        pictopath = imagefield.name
        mimetype = mimetypes.guess_type(pictopath)
        mimetype = mimetype[0] if mimetype else 'application/octet-stream'
        encoded = imagefield.read().encode('base64').replace("\n", '')
        return "%s;base64,%s" % (mimetype, encoded)
    except (IOError, ValueError), e:
        logger.warning(e)
        return ''
