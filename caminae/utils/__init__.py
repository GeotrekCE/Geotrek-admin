import math

from django.db import connection
from django.utils.timezone import utc


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
