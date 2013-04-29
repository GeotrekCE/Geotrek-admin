# -*- coding: utf-8 -*-
import csv
import math
from HTMLParser import HTMLParser

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import smart_str
from django.utils.html import strip_tags
from django.db.models.fields.related import ForeignKey, ManyToManyField, FieldDoesNotExist
from django.core.serializers.base import Serializer
from django.contrib.gis.geos import Point, LineString, MultiPoint, MultiLineString
from django.contrib.gis.geos.collections import GeometryCollection
from django.contrib.gis.db.models.fields import (GeometryField, GeometryCollectionField,
                                                 PointField, LineStringField,
                                                 MultiPointField, MultiLineStringField)

import gpxpy

from .templatetags.timesince import humanize_timesince
from . import shape_exporter


class DatatablesSerializer(Serializer):
    def serialize(self, queryset, **options):
        model = queryset.model
        columns = options.pop('fields')

        attr_getters = {}
        for field in columns:
            if hasattr(model, field + '_display'):
                attr_getters[field] = lambda obj, field: getattr(obj, field + '_display')
            else:
                modelfield = model._meta.get_field(field)
                if isinstance(modelfield, ForeignKey):
                    attr_getters[field] = lambda obj, field: unicode(getattr(obj, field) or _("None"))
                elif isinstance(modelfield, ManyToManyField):
                    attr_getters[field] = lambda obj, field: [unicode(o) for o in getattr(obj, field).all()] or _("None")
                else:
                    def fixfloat(obj, field):
                        value = getattr(obj, field)
                        if isinstance(value, float) and math.isnan(value):
                            value = 0.0
                        return value
                    attr_getters[field] = fixfloat
        # Build list with fields
        map_obj_pk = []
        data_table_rows = []
        for obj in queryset:
            row = [attr_getters[field](obj, field) for field in columns]
            data_table_rows.append(row)
            map_obj_pk.append(obj.pk)

        return {
            # aaData is the key looked up by dataTables
            'aaData': data_table_rows,
            'map_obj_pk': map_obj_pk,
        }


class CSVSerializer(Serializer):
    def serialize(self, queryset, **options):
        """
        Uses self.columns, containing fieldnames to produce the CSV.
        The header of the csv is made of the verbose name of each field
        Each column content is made using (by priority order):
            * <field_name>_csv_display
            * <field_name>_display
            * <field_name>
        """
        model = queryset.model
        columns = options.pop('fields')
        stream = options.pop('stream')
        ascii = options.get('ensure_ascii', True)

        html = HTMLParser()

        def proc_string(s):
            try:
                # Converts to unicode, remove HTML tags, convert HTML entities
                us = html.unescape(strip_tags(unicode(s)))
                if ascii:
                    return smart_str(us)
                return us
            except UnicodeDecodeError:
                return smart_str(s)

        headers = []
        for field in columns:
            c = getattr(model, '%s_verbose_name' % field, None)
            if c is None:
                try:
                    c = model._meta.get_field(field).verbose_name
                except FieldDoesNotExist:
                    c = _(field.title())
            headers.append(smart_str(unicode(c)))

        attr_getters = {}
        for field in columns:
            try:
                modelfield = model._meta.get_field(field)
            except FieldDoesNotExist:
                modelfield = None
            if isinstance(modelfield, ForeignKey):
                attr_getters[field] = lambda obj, field: proc_string(getattr(obj, field) or '')
            elif isinstance(modelfield, ManyToManyField):
                attr_getters[field] = lambda obj, field: ','.join([proc_string(o) for o in getattr(obj, field).all()] or '')
            else:
                def simple(obj, field):
                    value = getattr(obj, field + '_csv_display',
                                    getattr(obj, field + '_display', getattr(obj, field)))
                    if hasattr(value, '__iter__'):
                        value = ','.join([proc_string(value) for value in value])
                    return proc_string(value) if value is not None else ''
                attr_getters[field] = simple

        def get_lines():
            yield headers
            for obj in queryset:
                yield [attr_getters[field](obj, field) for field in columns]
        writer = csv.writer(stream)
        writer.writerows(get_lines())


class GPXSerializer(Serializer):
    """
    GPX serializer class. Very rough implementation, but better than inline code.
    """
    # TODO : this should definitely respect Serializer abstraction :
    # LineString -> Route with Point
    # Collection -> route with all merged

    def serialize(self, queryset, **options):
        gpx = gpxpy.gpx.GPX()

        stream = options.pop('stream')
        geom_field = options.pop('geom_field')

        for obj in queryset:
            geom = getattr(obj, geom_field)
            objtype = unicode(obj.__class__._meta.verbose_name)
            name = '[%s] %s' % (objtype, unicode(obj))

            description = ''
            objupdate = getattr(obj, 'date_update')
            if objupdate:
                description = _('Modified') + ': ' + humanize_timesince(objupdate)

            # geom.transform(settings.API_SRID, clone=True)) does not work as it looses the Z
            # All geometries will looses their SRID being convert to simple tuples
            # They must have the same SRID to be treated equally.
            # Converting at point level only avoid creating unused point only to carry SRID (could be a param too..)
            if geom:
                assert geom.srid == settings.SRID, "Invalid srid"
                geomToGPX(gpx, geom, name, description)
        stream.write(gpx.to_xml())


def geomToGPX(gpx, geom, name, description):
    """Convert a geometry to a gpx entity.
    Raise ValueError if it is not a Point, LineString or a collection of those

    Point -> add as a Way Point
    LineString -> add all Points in a Route
    Collection (of LineString or Point) -> add as a route, concatening all points
    """
    if isinstance(geom, Point):
        wp = point_to_GPX(geom)
        wp.name = name
        wp.description = description
        gpx.waypoints.append(wp)
    else:
        gpx_route = gpxpy.gpx.GPXRoute(name=name, description=description)
        gpx.routes.append(gpx_route)

        if isinstance(geom, LineString):
            gpx_route.points = lineString_to_GPX(geom)
        # Accept collections composed of Point and LineString mixed or not
        elif isinstance(geom, GeometryCollection):
            points = gpx_route.points
            for g in geom:
                if isinstance(g, Point):
                    points.append(point_to_GPX(g))
                elif isinstance(g, LineString):
                    points.extend(lineString_to_GPX(g))
                else:
                    raise ValueError("Unsupported geometry %s" % geom)
        else:
            raise ValueError("Unsupported geometry %s" % geom)


def lineString_to_GPX(geom):
    return [point_to_GPX(point, klass=gpxpy.gpx.GPXRoutePoint) for point in geom]


def point_to_GPX(point, klass=gpxpy.gpx.GPXWaypoint):
    """Should be a tuple with 3 coords or a Point"""
    # FIXME: suppose point are in the settings.SRID format
    # Set point SRID to such srid if invalid or missing

    if not isinstance(point, Point):
        point = Point(*point, srid=settings.SRID)
    elif (point.srid is None or point.srid < 0):
        point.srid = settings.SRID

    x, y = point.transform(4326, clone=True)  # transformation: gps uses 4326
    z = point.z  # transform looses the Z parameter - reassign it

    return klass(latitude=y, longitude=x, elevation=z)


class ZipShapeSerializer(Serializer):
    def start_object(self, *args, **kwargs):
        pass

    def serialize(self, queryset, **options):
        columns = options.pop('fields')
        stream = options.pop('stream')
        shp_creator = shape_exporter.ShapeCreator()
        self.create_shape(shp_creator, queryset, columns)
        stream.write(shp_creator.as_zip())

    def create_shape(self, shp_creator, queryset, columns):
        """Split a shapes into one or more shapes (one for point and one for linestring)"""
        fieldmap = shape_exporter.fieldmap_from_fields(queryset.model, columns)
        # Don't use this - projection does not work yet (looses z dimension)
        # srid_out = settings.API_SRID

        geo_field = shape_exporter.geo_field_from_model(queryset.model, 'geom')
        get_geom, geom_type, srid = shape_exporter.info_from_geo_field(geo_field)

        if geom_type.upper() in (GeometryField.geom_type, GeometryCollectionField.geom_type):

            by_points, by_linestrings, multipoints, multilinestrings = self.split_bygeom(queryset, geom_getter=get_geom)

            for split_qs, split_geom_field in ((by_points, PointField),
                                               (by_linestrings, LineStringField),
                                               (multipoints, MultiPointField),
                                               (multilinestrings, MultiLineStringField)):
                if len(split_qs) == 0:
                    continue
                split_geom_type = split_geom_field.geom_type
                shp_filepath = shape_exporter.shape_write(split_qs, fieldmap, get_geom, split_geom_type, srid)

                shp_creator.add_shape('shp_download_%s' % split_geom_type.lower(), shp_filepath)
        else:
            shp_filepath = shape_exporter.shape_write(queryset, fieldmap, get_geom, geom_type, srid)

            shp_creator.add_shape('shp_download', shp_filepath)

    def split_bygeom(self, iterable, geom_getter=lambda x: x.geom):
        """Split an iterable in two list (points, linestring)"""
        points, linestrings, multipoints, multilinestrings = [], [], [], []

        for x in iterable:
            geom = geom_getter(x)
            if geom is None:
                pass
            elif isinstance(geom, GeometryCollection):
                # Duplicate object, shapefile do not support geometry collections !
                subpoints, sublines, pp, ll = self.split_bygeom(geom, geom_getter=lambda geom: geom)
                if subpoints:
                    clone = x.__class__.objects.get(pk=x.pk)
                    clone.geom = MultiPoint(subpoints, srid=geom.srid)
                    multipoints.append(clone)
                if sublines:
                    clone = x.__class__.objects.get(pk=x.pk)
                    clone.geom = MultiLineString(sublines, srid=geom.srid)
                    multilinestrings.append(clone)
            elif isinstance(geom, Point):
                points.append(x)
            elif isinstance(geom, LineString):
                linestrings.append(x)
            else:
                raise ValueError("Only LineString and Point geom should be here. Got %s for pk %d" % (geom, x.pk))
        return points, linestrings, multipoints, multilinestrings
