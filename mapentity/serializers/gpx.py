# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.serializers.base import Serializer
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos.collections import GeometryCollection
from django.contrib.gis.geos import Point, LineString

import gpxpy

from ..templatetags.timesince import humanize_timesince


class GPXSerializer(Serializer):
    """
    GPX serializer class. Very rough implementation, but better than inline code.
    """
    # TODO : this should definitely respect Serializer abstraction :
    # LineString -> Route with Point
    # Collection -> One route/waypoint per item
    def __init__(self, *args, **kwargs):
        self.gpx = None

    def serialize(self, queryset, **options):
        self.gpx = gpxpy.gpx.GPX()

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
            if geom:
                assert geom.srid == settings.SRID, "Invalid srid"
                self.geomToGPX(geom, name, description)
        stream.write(self.gpx.to_xml())

    def _point_to_GPX(self, point, klass=gpxpy.gpx.GPXWaypoint):
        if isinstance(point, (tuple, list)):
            point = Point(*point, srid=settings.SRID)
        newpoint = point.transform(4326, clone=True)  # transformation: gps uses 4326
        # transform looses the Z parameter
        return klass(latitude=newpoint.y, longitude=newpoint.x, elevation=point.z)

    def geomToGPX(self, geom, name, description):
        """Convert a geometry to a gpx entity.
        Raise ValueError if it is not a Point, LineString or a collection of those

        Point -> add as a Way Point
        LineString -> add all Points in a Route
        Collection (of LineString or Point) -> add as a route, concatening all points
        """
        if isinstance(geom, GeometryCollection):
            for i, g in enumerate(geom):
                self.geomToGPX(g, u"%s (%s)" % (name, i), description)
        elif isinstance(geom, Point):
            wp = self._point_to_GPX(geom)
            wp.name = name
            wp.description = description
            self.gpx.waypoints.append(wp)
        elif isinstance(geom, LineString):
            gpx_route = gpxpy.gpx.GPXRoute(name=name, description=description)
            gpx_route.points = [self._point_to_GPX(point, klass=gpxpy.gpx.GPXRoutePoint) for point in geom]
            self.gpx.routes.append(gpx_route)
        else:
            raise ValueError("Unsupported geometry %s" % geom)
