import fiona
from django.conf import settings
from django.contrib.gis.geos import LineString, Point


def update_gis(input_file_path: str, output_file_path: str, new_properties: dict):
    """
    Utility function that reads a GIS file (GeoPackage or Shapefile), update some properties,
    then write a new shapefile (typically in /tmp). Useful to test specific property values.
    """

    with fiona.open(input_file_path) as source:
        with fiona.open(
            output_file_path,
            mode="w",
            crs=source.crs,
            driver=source.driver,
            schema=source.schema,
        ) as dest:
            for feat in source:
                dest.write(
                    fiona.Feature(
                        geometry=feat.geometry,
                        properties={**feat.properties, **new_properties},
                    )
                )


def _get_y(y):
    return 6587552.2 + y


def _get_x(x):
    return 489353.59 + x


class LineStringInBounds(LineString):
    """
    A LineString that is guaranteed to be within the bounds of default projection.
    Useful for tests that require geometries within certain bounds,
    because ST_LENGTHSPHEROID can compute very bad data if coords is out of bounds.
    """

    def __init__(self, *args, **kwargs):
        # Define a simple LineString within typical world bounds
        kwargs.setdefault("srid", settings.SRID)  # Default SRID for French Lambert-93
        coords = [[_get_x(point[0]), _get_y(point[1])] for point in args]
        super().__init__(*coords, **kwargs)


class PointInBounds(Point):
    """
    A Point that is guaranteed to be within the bounds of default projection.
    Useful for tests that require geometries within certain bounds,
    because ST_LENGTHSPHEROID can compute very bad data if coords is out of bounds.
    """

    def __init__(self, x=0, y=0, **kwargs):
        kwargs.setdefault("srid", settings.SRID)
        super().__init__((_get_x(x), _get_y(y)), **kwargs)
