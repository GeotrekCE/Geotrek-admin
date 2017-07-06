from __future__ import unicode_literals

from coreapi.document import Field
from rest_framework.filters import BaseFilterBackend
from rest_framework_gis.filters import InBBOXFilter, DistanceToPointFilter


class GeotrekQueryParamsFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset

    def get_schema_fields(self, view):
        field_dim = Field(name='dim', required=False,
                          description='Set geometry dimension (2 by default for 2D, 3 for 3D)',
                          example=3, type='integer')
        field_language = Field(name='language', required=False,
                               description="Set language for translation. 'all' by default",
                               example="fr")
        field_format = Field(name='format', required=False,
                             description="Set output format (json / geojson). JSON by default",
                             example="geojson")
        return field_dim, field_language, field_format


class GeotrekInBBoxFilter(InBBOXFilter):
    """
    Override DRF gis InBBOXFilter with coreapi field descriptors
    """

    def get_schema_fields(self, view):
        field_in_bbox = Field(name=self.bbox_param, required=False,
                              description='Filter elements contained in bbox formatted like SW-lng,SW-lat,NE-lng,NE-lat',
                              example='1.15,46.1,1.56,47.6')

        return field_in_bbox,


class GeotrekDistanceToPointFilter(DistanceToPointFilter):
    """
    Override DRF gis DistanceToPointFilter with coreapi field descriptors
    """

    def get_schema_fields(self, view):
        field_dist = Field(name=self.dist_param, required=False,
                           description='Max distance in meters between point and elements',
                           type='number',
                           example='XXX')
        field_point = Field(name=self.point_param, required=False,
                            description='Reference point to compute distance',
                            example='YES MAN', )
        return field_dist, field_point
