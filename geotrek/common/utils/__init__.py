import logging

from django.conf import settings
from django.contrib.gis.db.models.functions import Intersection, LineLocatePoint
from django.contrib.gis.gdal import SpatialReference
from django.contrib.gis.measure import Distance
from django.db import connection
from django.db.models.base import ModelBase
from django.db.models.expressions import Func
from django.utils.translation import pgettext
from pytz import utc

from geotrek.common.functions import DumpGeom, StartPoint

logger = logging.getLogger(__name__)


class classproperty:
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, instance, owner):
        return self.getter(owner)


# This one come from pyramid
# https://github.com/Pylons/pyramid/blob/master/pyramid/decorator.py
class reify:
    """Put the result of a method which uses this (non-data)
    descriptor decorator in the instance dict after the first call,
    effectively replacing the decorator with an instance variable."""

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except AttributeError:
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


def dbnow():
    with connection._nodb_cursor() as cursor:
        cursor.execute("SELECT statement_timestamp() AT TIME ZONE 'UTC';")
        row = cursor.fetchone()
    return row[0].replace(tzinfo=utc)


def sqlfunction(function, *args):
    """Executes the SQL function with the specified args, and returns the result."""
    sql = "{}({})".format(function, ",".join(args))
    logger.debug(sql)
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    if len(result) == 1:
        return result[0]
    return result


def uniquify(values):
    """
    Return unique values, order preserved
    """
    unique = []
    [unique.append(i) for i in values if i not in unique]
    return unique


def queryset_or_model(queryset, model):
    # It is very important to test queryset Noneness with `is None` because the queryset gets otherwise
    # evaluated in bool() context. So here is a function not to forget that.
    if queryset is not None:
        return queryset
    else:
        return model


def queryset_or_all_objects(queryset, model):
    # It is very important to test queryset Noneness with `is None` because the queryset gets otherwise
    # evaluated in bool() context. So here is a function not to forget that.
    if queryset is None:
        queryset = model.objects
        if hasattr(queryset, "existing"):
            queryset = queryset.existing()
    return queryset


def intersecting(qs, obj, distance=None, ordering=True, field="geom", defer=None):
    """Small helper to filter all model instances by geometry intersection"""
    if isinstance(qs, ModelBase):
        qs = qs.objects
        if hasattr(qs, "existing"):
            qs = qs.existing()
    if not obj.geom:
        return qs.none()
    if distance is None:
        distance = obj.distance(qs.model)
    if distance:
        qs = qs.filter(**{f"{field}__dwithin": (obj.geom, Distance(m=distance))})
    else:
        qs = qs.filter(**{f"{field}__intersects": obj.geom})
        if obj.geom.geom_type == "LineString" and ordering:
            qs = qs.order_by(
                LineLocatePoint(
                    obj.geom, StartPoint(DumpGeom(Intersection(obj.geom, field)))
                )
            )

    if obj.__class__ == qs.model:
        # Prevent self intersection
        qs = qs.exclude(pk=obj.pk)
    if defer:
        qs = qs.defer(*defer)

    return qs


def format_coordinates(geom):
    if settings.DISPLAY_SRID in [4326, 3857]:  # WGS84 formatting
        location = geom.centroid.transform(4326, clone=True)
        if settings.DISPLAY_COORDS_AS_DECIMALS:
            if location.y > 0:
                degreelong = f"{location.y:0.6f}°N"
            else:
                degreelong = "%0.6f°S" % -location.y
            if location.x > 0:
                degreelat = f"{location.x:0.6f}°E"
            else:
                degreelat = "%0.6f°W" % -location.x
            result = f"{degreelong}, {degreelat}"

        else:
            rounded_lat_sec = round(abs(location.y) * 3600)
            rounded_lng_sec = round(abs(location.x) * 3600)
            result = (
                "{lat_deg}°{lat_min:02d}'{lat_sec:02d}\" {lat_card} / "
                + "{lng_deg}°{lng_min:02d}'{lng_sec:02d}\" {lng_card}"
            ).format(
                lat_deg=(rounded_lat_sec // 3600),
                lat_min=((rounded_lat_sec // 60) % 60),
                lat_sec=(rounded_lat_sec % 60),
                lat_card=pgettext("North", "N")
                if location.y >= 0
                else pgettext("South", "S"),
                lng_deg=(rounded_lng_sec // 3600),
                lng_min=((rounded_lng_sec // 60) % 60),
                lng_sec=(rounded_lng_sec % 60),
                lng_card=pgettext("East", "E")
                if location.x >= 0
                else pgettext("West", "W"),
            )
    else:
        location = geom.centroid.transform(settings.DISPLAY_SRID, clone=True)
        result = f"X : {round(location.x):07d} / Y : {round(location.y):07d}"
    return result


def collate_c(field):
    field_collate = Func(
        field, function="C", template='(%(expressions)s) COLLATE "%(function)s"'
    )
    return field_collate


def spatial_reference():
    return f"{SpatialReference(settings.DISPLAY_SRID).name}"


def simplify_coords(coords):
    if isinstance(coords, list | tuple):
        return [simplify_coords(coord) for coord in coords]
    elif isinstance(coords, float):
        return round(coords, 7)
    msg = f"Param is {type(coords)}. Should be <list>, <tuple> or <float>"
    raise Exception(msg)


def leaflet_bounds(bbox):
    return [[bbox[1], bbox[0]], [bbox[3], bbox[2]]]
