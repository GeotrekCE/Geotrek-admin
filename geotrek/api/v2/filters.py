from __future__ import unicode_literals

from rest_framework_gis.filters import InBBOXFilter, DistanceToPointFilter
from coreapi.document import Field


class GeotrekInBBoxFilter(InBBOXFilter):
    """
    Override DRF gis InBBOXFilter with coreapi field descriptors
    """
    def get_schema_fields(self, view):
        field_in_bbox = Field(name=self.bbox_param, required=False,
                              description='Filter elements contained in bbox',
                              example='XXX')
        field_dim = Field(name='dim', required=False,
                          description='Set geometry dimension (2 by default for 2D, 3 for 3D)',
                          example=3, type=int())
        return field_in_bbox, field_dim


class GeotrekDistanceToPointFilter(DistanceToPointFilter):
    """
    Override DRF gis DistanceToPointFilter with coreapi field descriptors
    """
    def get_schema_fields(self, view):
        field_dist = Field(name=self.dist_param, required=False,
                           description='Distance max between point and elements',
                           example='XXX')
        field_point = Field(name=self.point_param, required=False,
                            description='Reference point to compute distance',
                            example='YES MAN', )
        return field_dist, field_point