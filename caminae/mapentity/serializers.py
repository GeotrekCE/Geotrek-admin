# -*- coding: utf-8 -*-
import gpxpy

from django.conf import settings
from django.core.serializers.base import Serializer
from django.contrib.gis.geos.point import Point
from django.contrib.gis.geos.linestring import LineString
from django.contrib.gis.geos.collections import GeometryCollection



class GPXSerializer(Serializer):
    """
    GPX serializer class. Very rough implementation, but better than inline code.
    """
    def serialize(self, queryset, **options):
        gpx = gpxpy.gpx.GPX()
        
        geom_field = options.pop('geom_field')

        for obj in queryset:
            geom = getattr(obj, geom_field)
            
            # geom.transform(settings.API_SRID, clone=True)) does not work as it looses the Z
            # All geometries will looses their SRID being convert to simple tuples
            # They must have the same SRID to be treated equally.
            # Converting at point level only avoid creating unused point only to carry SRID (could be a param too..)
            if geom:
                assert geom.srid == settings.SRID, "Invalid srid"
                geomToGPX(gpx, geom)
        return gpx.to_xml()


#TODO : this should definitely respect Serializer abstraction :
# LineString -> Route with Point
# Collection -> route with all merged
def geomToGPX(self, gpx, geom):
    """Convert a geometry to a gpx entity.
    Raise ValueError if it is not a Point, LineString or a collection of those

    Point -> add as a Way Point
    LineString -> add all Points in a Route
    Collection (of LineString or Point) -> add as a route, concatening all points
    """
    if isinstance(geom, Point):
        gpx.waypoints.append(point_to_GPX(geom))
    else:
        gpx_route = gpxpy.gpx.GPXRoute()
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
    return [ point_to_GPX(point) for point in geom ]

def point_to_GPX(point):
    """Should be a tuple with 3 coords or a Point"""
    # FIXME: suppose point are in the settings.SRID format
    # Set point SRID to such srid if invalid or missing

    if not isinstance(point, Point):
        point = Point(*point, srid=settings.SRID)
    elif (point.srid is None or point.srid < 0):
        point.srid = settings.SRID

    x, y = point.transform(4326, clone=True) # transformation: gps uses 4326
    z = point.z # transform looses the Z parameter - reassign it

    return gpxpy.gpx.GPXWaypoint(latitude=y, longitude=x, elevation=z)
