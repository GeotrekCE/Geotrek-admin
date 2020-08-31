"""

   Zoning models
   (not MapEntity : just layers, on which intersections with objects is done in triggers)

"""
from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import ugettext_lazy as _
from geotrek.common.utils import uniquify, intersecting
from geotrek.maintenance.models import Intervention, Project
from geotrek.tourism.models import TouristicContent, TouristicEvent
from operator import attrgetter

from geotrek.core.models import Topology, Path

if 'geotrek.diving' in settings.INSTALLED_APPS:
    from geotrek.diving.models import Dive
if 'geotrek.signage' in settings.INSTALLED_APPS:
    from geotrek.signage.models import Blade


class RestrictedAreaType(models.Model):
    name = models.CharField(max_length=200, verbose_name=_("Name"))

    class Meta:
        verbose_name = _("Restricted area type")

    def __str__(self):
        return self.name


class RestrictedAreaManager(models.Manager):
    def get_queryset(self):
        return super(RestrictedAreaManager, self).get_queryset().select_related('area_type')


class RestrictedArea(models.Model):
    name = models.CharField(max_length=250, verbose_name=_("Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    area_type = models.ForeignKey(RestrictedAreaType, verbose_name=_("Restricted area"), on_delete=models.CASCADE)
    published = models.BooleanField(verbose_name=_("Published"), default=True, help_text=_("Visible on Geotrek-rando"))

    # Override default manager
    objects = RestrictedAreaManager()

    class Meta:
        ordering = ['area_type', 'name']
        verbose_name = _("Restricted area")
        verbose_name_plural = _("Restricted areas")

    def __str__(self):
        return "{} - {}".format(self.area_type.name, self.name)


class RestrictedAreaEdge(Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True, on_delete=models.CASCADE)
    restricted_area = models.ForeignKey(RestrictedArea, verbose_name=_("Restricted area"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Restricted area edge")
        verbose_name_plural = _("Restricted area edges")

    def __str__(self):
        return "{}: {}".format(_("Restricted area edge"), self.restricted_area)

    @classmethod
    def path_area_edges(cls, path):
        return cls.objects.existing()\
                          .select_related('restricted_area')\
                          .select_related('restricted_area__area_type')\
                          .filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_area_edges(cls, topology):
        return cls.overlapping(topology)\
                  .select_related('restricted_area')\
                  .select_related('restricted_area__area_type')


if settings.TREKKING_TOPOLOGY_ENABLED:
    Path.add_property('area_edges', RestrictedAreaEdge.path_area_edges, _("Restricted area edges"))
    Path.add_property('areas', lambda self: uniquify(map(attrgetter('restricted_area'), self.area_edges)),
                      _("Restricted areas"))
    Topology.add_property('area_edges', RestrictedAreaEdge.topology_area_edges, _("Restricted area edges"))
    Topology.add_property('areas', lambda self: uniquify(
        intersecting(RestrictedArea, self)) if self.ispoint() else uniquify(
        map(attrgetter('restricted_area'), self.area_edges)), _("Restricted areas"))
    Intervention.add_property('area_edges', lambda self: self.target.area_edges if self.target and self.target else [],
                              _("Restricted area edges"))
    Intervention.add_property('areas', lambda self: self.target.areas if self.target and self.target else [],
                              _("Restricted areas"))
    Project.add_property('area_edges', lambda self: self.edges_by_attr('area_edges'), _("Restricted area edges"))
    Project.add_property('areas', lambda self: uniquify(map(attrgetter('restricted_area'), self.area_edges)),
                         _("Restricted areas"))
else:
    Topology.add_property('areas', lambda self: uniquify(intersecting(RestrictedArea, self, distance=0)),
                          _("Restricted areas"))
    Project.add_property('areas', lambda self: uniquify(intersecting(RestrictedArea, self, distance=0)),
                         _("Restricted areas"))
    Intervention.add_property('areas', lambda self: uniquify(intersecting(RestrictedArea, self, distance=0)),
                              _("Restricted areas"))

TouristicContent.add_property('areas', lambda self: intersecting(RestrictedArea, self, distance=0),
                              _("Restricted areas"))
TouristicEvent.add_property('areas', lambda self: intersecting(RestrictedArea, self, distance=0),
                            _("Restricted areas"))
if 'geotrek.diving' in settings.INSTALLED_APPS:
    Dive.add_property('areas', lambda self: uniquify(intersecting(RestrictedArea, self, distance=0)), _("Restricted areas"))
if 'geotrek.signage' in settings.INSTALLED_APPS:
    Blade.add_property('areas', lambda self: self.signage.areas, _("Restricted areas"))


class City(models.Model):
    code = models.CharField(primary_key=True, max_length=6)
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    published = models.BooleanField(verbose_name=_("Published"), default=True, help_text=_("Visible on Geotrek-rando"))

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")
        ordering = ['name']

    def __str__(self):
        return self.name


class CityEdge(Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True, on_delete=models.CASCADE)

    city = models.ForeignKey(City, verbose_name=_("City"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("City edge")
        verbose_name_plural = _("City edges")

    def __str__(self):
        return "{}: {}".format(_("City edge"), self.city)

    @classmethod
    def path_city_edges(cls, path):
        return cls.objects.existing().select_related('city').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_city_edges(cls, topology):
        return cls.overlapping(topology).select_related('city')


if settings.TREKKING_TOPOLOGY_ENABLED:
    Path.add_property('city_edges', CityEdge.path_city_edges, _("City edges"))
    Path.add_property('cities', lambda self: uniquify(map(attrgetter('city'), self.city_edges)), _("Cities"))
    Topology.add_property('city_edges', CityEdge.topology_city_edges, _("City edges"))
    Topology.add_property('cities',
                          lambda self: uniquify(intersecting(City, self, distance=0)), _("Cities"))
    Intervention.add_property('city_edges', lambda self: self.target.city_edges if self.target else [],
                              _("City edges"))
    Intervention.add_property('cities', lambda self: self.target.cities if self.target else [], _("Cities"))
    Project.add_property('city_edges', lambda self: self.edges_by_attr('city_edges'), _("City edges"))
    Project.add_property('cities', lambda self: uniquify(map(attrgetter('city'), self.city_edges)), _("Cities"))
else:
    Topology.add_property('cities', lambda self: uniquify(intersecting(City, self, distance=0)), _("Cities"))
    Project.add_property('cities', lambda self: uniquify(intersecting(City, self, distance=0)), _("Cities"))
    Intervention.add_property('cities', lambda self: uniquify(intersecting(City, self, distance=0)), _("Cities"))

TouristicContent.add_property('cities', lambda self: intersecting(City, self, distance=0), _("Cities"))
TouristicEvent.add_property('cities', lambda self: intersecting(City, self, distance=0), _("Cities"))
if 'geotrek.diving' in settings.INSTALLED_APPS:
    Dive.add_property('cities', lambda self: uniquify(intersecting(City, self, distance=0)), _("Cities"))
if 'geotrek.signage' in settings.INSTALLED_APPS:
    Blade.add_property('cities', lambda self: self.signage.cities, _("Cities"))


class District(models.Model):
    name = models.CharField(max_length=128, verbose_name=_("Name"))
    geom = models.MultiPolygonField(srid=settings.SRID, spatial_index=False)
    published = models.BooleanField(verbose_name=_("Published"), default=True, help_text=_("Visible on Geotrek-rando"))

    class Meta:
        verbose_name = _("District")
        verbose_name_plural = _("Districts")
        ordering = ['name']

    def __str__(self):
        return self.name


class DistrictEdge(Topology):
    topo_object = models.OneToOneField(Topology, parent_link=True, on_delete=models.CASCADE)
    district = models.ForeignKey(District, verbose_name=_("District"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("District edge")
        verbose_name_plural = _("District edges")

    def __str__(self):
        return "{}: {}".format(_("District edge"), self.district)

    @classmethod
    def path_district_edges(cls, path):
        return cls.objects.existing().select_related('district').filter(aggregations__path=path).distinct('pk')

    @classmethod
    def topology_district_edges(cls, topology):
        return cls.overlapping(topology).select_related('district')


if settings.TREKKING_TOPOLOGY_ENABLED:
    Path.add_property('district_edges', DistrictEdge.path_district_edges, _("District edges"))
    Path.add_property('districts', lambda self: uniquify(map(attrgetter('district'), self.district_edges)),
                      _("Districts"))
    Topology.add_property('district_edges', DistrictEdge.topology_district_edges, _("District edges"))
    Topology.add_property('districts', lambda self: uniquify(
        intersecting(District, self)) if self.ispoint() else uniquify(
        map(attrgetter('district'), self.district_edges)), _("Districts"))
    Intervention.add_property('district_edges', lambda self: self.target.district_edges if self.target else [], _("District edges"))
    Intervention.add_property('districts', lambda self: self.target.districts if self.target else [],
                              _("Districts"))
    Project.add_property('district_edges', lambda self: self.edges_by_attr('district_edges'), _("District edges"))
    Project.add_property('districts', lambda self: uniquify(map(attrgetter('district'), self.district_edges)),
                         _("Districts"))
else:
    Topology.add_property('districts', lambda self: uniquify(intersecting(District, self, distance=0)),
                          _("Districts"))
    Project.add_property('districts', lambda self: uniquify(intersecting(District, self, distance=0)),
                         _("Districts"))
    Intervention.add_property('districts', lambda self: uniquify(intersecting(District, self, distance=0)),
                              _("Districts"))

TouristicContent.add_property('districts', lambda self: intersecting(District, self, distance=0), _("Districts"))
TouristicEvent.add_property('districts', lambda self: intersecting(District, self, distance=0), _("Districts"))
if 'geotrek.diving' in settings.INSTALLED_APPS:
    Dive.add_property('districts', lambda self: uniquify(intersecting(District, self, distance=0)), _("Districts"))
if 'geotrek.signage' in settings.INSTALLED_APPS:
    Blade.add_property('districts', lambda self: self.signage.districts, _("Districts"))
