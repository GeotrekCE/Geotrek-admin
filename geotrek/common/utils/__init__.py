import math
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


# This one come from pyramid
# https://github.com/Pylons/pyramid/blob/master/pyramid/decorator.py
class reify(object):

    """ Put the result of a method which uses this (non-data)
    descriptor decorator in the instance dict after the first call,
    effectively replacing the decorator with an instance variable."""

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:  # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


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


def elevation_profile(geometry, precision=None):
    """Extract elevation profile from a 3D geometry.

    :precision:  geometry sampling in meters
    """
    precision = precision or settings.ALTIMETRIC_PROFILE_PRECISION

    cursor = connection.cursor()
    # First, check if table mnt exists
    cursor.execute("SELECT * FROM pg_tables WHERE tablename='mnt';")
    exists = len(cursor.fetchall()) == 1
    if not exists:
        return []

    if geometry.geom_type == 'MultiLineString':
        profile = []
        for subcoords in geometry.coords:
            subline = LineString(subcoords)
            subprofile = elevation_profile(subline)
            profile.extend(subprofile)
        return profile

    # Build elevation profile from linestring and DEM
    # http://blog.mathieu-leplatre.info/drape-lines-on-a-dem-with-postgis.html
    sql = """
    WITH line AS
        (SELECT '%(ewkt)s'::geometry AS geom),
      middlesteps AS
        (SELECT generate_series(%(precision)s, ST_Length(line.geom)::int - %(precision)s, %(precision)s) as i FROM line),
      fractions AS
        (SELECT i / ST_Length(line.geom) AS fraction FROM middlesteps, line),
      sublines AS
        -- Cut line at each step
        (SELECT ST_Line_Substring(line.geom, 0.0, fraction) AS geom
         FROM fractions, line),
      points2d AS
        (SELECT ST_StartPoint(geom) as subline, ST_StartPoint(geom) as geom FROM line
         UNION
         SELECT geom as subline, ST_EndPoint(geom) as geom FROM sublines
         UNION
         SELECT geom as subline, ST_EndPoint(geom) as geom FROM line),
      cells AS
        -- Get DEM elevation for each
        (SELECT p.subline, p.geom AS geom, ST_Value(mnt.rast, 1, p.geom) AS val
         FROM points2d p, mnt
         WHERE ST_Intersects(mnt.rast, p.geom))
    SELECT coalesce(ST_Length(cells.subline), 0) as abscissa,
           ST_X(ST_Transform(cells.geom, %(api_srid)s)) as lng,
           ST_Y(ST_Transform(cells.geom, %(api_srid)s)) as lat,
           cells.val as h
    FROM cells
    ORDER BY abscissa
    """ % {'ewkt': geometry.ewkt, 'precision': precision, 'api_srid': settings.API_SRID}
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


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
    return abs(v1 - v2) < 10 ** -precision


def smart_urljoin(base, path):
    if base[-1] != '/':
        base += '/'
    if path[0] == '/':
        path = path[1:]
    return urljoin(base, path)
