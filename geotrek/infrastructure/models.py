import os

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from extended_choices import Choices

from geotrek.authent.models import StructureRelated, StructureOrNoneRelated
from geotrek.common.utils import classproperty, intersecting, queryset_or_all_objects, queryset_or_model
from geotrek.common.mixins.models import (BasePublishableMixin, OptionalPictogramMixin, TimeStampedModelMixin,
                                          GeotrekMapEntityMixin)
from geotrek.core.models import Topology, Path
from geotrek.infrastructure.managers import InfrastructureGISManager

INFRASTRUCTURE_TYPES = Choices(
    ('BUILDING', 'A', _("Building")),
    ('FACILITY', 'E', _("Facility")),
)


class InfrastructureType(TimeStampedModelMixin, StructureOrNoneRelated, OptionalPictogramMixin):
    """ Types of infrastructures (bridge, WC, stairs, ...) """
    label = models.CharField(max_length=128)
    type = models.CharField(max_length=1, choices=INFRASTRUCTURE_TYPES)

    class Meta:
        verbose_name = _("Infrastructure Type")
        verbose_name_plural = _("Infrastructure Types")
        ordering = ['label', 'type']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label

    def get_pictogram_url(self):
        pictogram_url = super().get_pictogram_url()
        if pictogram_url:
            return pictogram_url
        return os.path.join(settings.STATIC_URL, 'infrastructure/picto-infrastructure.png')


class InfrastructureCondition(TimeStampedModelMixin, StructureOrNoneRelated):
    label = models.CharField(verbose_name=_("Name"), max_length=250)

    class Meta:
        verbose_name = _("Infrastructure Condition")
        verbose_name_plural = _("Infrastructure Conditions")
        ordering = ('label',)

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label


class InfrastructureMaintenanceDifficultyLevel(TimeStampedModelMixin, StructureOrNoneRelated):
    label = models.CharField(verbose_name=_("Label"), max_length=250)

    class Meta:
        verbose_name = _("Maintenance difficulty")
        verbose_name_plural = _("Maintenance difficulty levels")
        ordering = ('label',)
        unique_together = ('label', 'structure')

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label


class InfrastructureUsageDifficultyLevel(TimeStampedModelMixin, StructureOrNoneRelated):
    label = models.CharField(verbose_name=_("Label"), unique=True, max_length=250)

    class Meta:
        verbose_name = _("Usage difficulty")
        verbose_name_plural = _("Usage difficulty levels")
        ordering = ('label',)
        unique_together = ('label', 'structure')

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label


class BaseInfrastructure(BasePublishableMixin, Topology, StructureRelated):
    """ A generic infrastructure in the park """
    topo_object = models.OneToOneField(Topology, parent_link=True,
                                       on_delete=models.CASCADE)

    name = models.CharField(max_length=128,
                            help_text=_("Reference, code, ..."), verbose_name=_("Name"))
    description = models.TextField(blank=True,
                                   verbose_name=_("Description"), help_text=_("Specificites"))
    condition = models.ForeignKey(InfrastructureCondition,
                                  verbose_name=_("Condition"), blank=True, null=True,
                                  on_delete=models.SET_NULL)
    implantation_year = models.PositiveSmallIntegerField(verbose_name=_("Implantation year"), null=True)
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)
    provider = models.CharField(verbose_name=_("Provider"), db_index=True, max_length=1024, blank=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @property
    def implantation_year_display(self):
        return "{}".format(self.implantation_year) if self.implantation_year else ""

    @property
    def name_display(self):
        s = '<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk, self.get_detail_url(),
                                                              self,
                                                              self)
        if self.published:
            s = '<span class="badge badge-success" title="%s">&#x2606;</span> ' % _("Published") + s
        return s

    @property
    def name_csv_display(self):
        return str(self)

    @property
    def type_display(self):
        return str(self.type)

    @property
    def cities_display(self):
        return [str(c) for c in self.cities] if hasattr(self, 'cities') else []

    @classproperty
    def cities_verbose_name(cls):
        return _("Cities")

    def distance(self, to_cls):
        """Distance to associate this site to another class"""
        return settings.TREK_INFRASTRUCTURE_INTERSECTION_MARGIN


class Infrastructure(BaseInfrastructure, GeotrekMapEntityMixin):
    """ An infrastructure in the park, which is not of type SIGNAGE """
    type = models.ForeignKey(InfrastructureType, related_name="infrastructures", verbose_name=_("Type"), on_delete=models.CASCADE)
    objects = InfrastructureGISManager()
    maintenance_difficulty = models.ForeignKey(InfrastructureMaintenanceDifficultyLevel,
                                               verbose_name=_("Maintenance difficulty"),
                                               help_text=_("Danger level of infrastructure maintenance"),
                                               blank=True, null=True,
                                               on_delete=models.SET_NULL,
                                               related_name='infrastructures_set')
    usage_difficulty = models.ForeignKey(InfrastructureUsageDifficultyLevel,
                                         verbose_name=_("Usage difficulty"),
                                         help_text=_("Danger level of end users' infrastructure usage"),
                                         blank=True, null=True,
                                         on_delete=models.SET_NULL,
                                         related_name='infrastructures_set')
    accessibility = models.TextField(verbose_name=_("Accessibility"), blank=True)

    geometry_types_allowed = ["LINESTRING", "POINT"]

    class Meta:
        verbose_name = _("Infrastructure")
        verbose_name_plural = _("Infrastructures")

    @classmethod
    def path_infrastructures(cls, path):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            return cls.objects.existing().filter(aggregations__path=path).distinct('pk')
        else:
            area = path.geom.buffer(settings.TREK_INFRASTRUCTURE_INTERSECTION_MARGIN)
            return cls.objects.existing().filter(geom__intersects=area)

    @classmethod
    def topology_infrastructures(cls, topology, queryset=None):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            qs = cls.overlapping(topology, all_objects=queryset)
        else:
            area = topology.geom.buffer(settings.TREK_INFRASTRUCTURE_INTERSECTION_MARGIN)
            qs = queryset_or_all_objects(queryset, cls)
            qs = qs.filter(geom__intersects=area)
        return qs

    @classmethod
    def published_topology_infrastructure(cls, topology):
        return cls.topology_infrastructures(topology).filter(published=True)

    @classmethod
    def tourism_infrastructures(cls, tourism_obj, queryset=None):
        return intersecting(qs=queryset_or_model(queryset, cls), obj=tourism_obj)

    @classmethod
    def outdoor_infrastructures(cls, outdoor_obj, queryset=None):
        return intersecting(qs=queryset_or_model(queryset, cls), obj=outdoor_obj)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for trek in self.treks.all():
            trek.save()

    def delete(self, *args, **kwargs):
        for trek in self.treks.all():
            trek.save()
        super().delete(*args, **kwargs)


Path.add_property('infrastructures', lambda self: Infrastructure.path_infrastructures(self), _("Infrastructures"))
Topology.add_property('infrastructures', Infrastructure.topology_infrastructures, _("Infrastructures"))
Topology.add_property('published_infrastructures', Infrastructure.published_topology_infrastructure,
                      _("Published Infrastructures"))
