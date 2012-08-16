import math

from django.db import connection
from django.conf import settings
from django.utils.timezone import utc
from django.contrib.gis.geos import GEOSException, fromstr


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


def wkt_to_geom(wkt):
    try:
        geom = fromstr(wkt, srid=settings.API_SRID)
        geom.transform(settings.SRID)
        dim = 3
        extracoords = ' 0.0' * (dim - 2)  # add missing dimensions
        wkt3d = geom.wkt.replace(',', extracoords + ',')
        return wkt3d
    except (GEOSException, TypeError, ValueError):
        return None
