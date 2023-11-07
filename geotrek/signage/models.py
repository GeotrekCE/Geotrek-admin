import os

from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _, pgettext_lazy

from django.conf import settings

from geotrek.authent.models import StructureOrNoneRelated
from geotrek.common.mixins.models import AddPropertyMixin, NoDeleteMixin, OptionalPictogramMixin, GeotrekMapEntityMixin, TimeStampedModelMixin
from geotrek.common.models import Organism
from geotrek.common.signals import log_cascade_deletion
from geotrek.common.utils import (
    classproperty, format_coordinates, collate_c, spatial_reference, intersecting, queryset_or_model, queryset_or_all_objects
)

from geotrek.core.models import Topology, Path

from geotrek.infrastructure.models import BaseInfrastructure
from geotrek.signage.managers import SignageGISManager

from geotrek.zoning.mixins import ZoningPropertiesMixin


class Sealing(TimeStampedModelMixin, StructureOrNoneRelated):
    """ A sealing linked with a signage"""
    label = models.CharField(verbose_name=_("Name"), max_length=250)

    class Meta:
        verbose_name = _("Sealing")
        verbose_name_plural = _("Sealings")

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label


class SignageType(TimeStampedModelMixin, StructureOrNoneRelated, OptionalPictogramMixin):
    """ Types of infrastructures (bridge, WC, stairs, ...) """
    label = models.CharField(max_length=128)

    class Meta:
        verbose_name = _("Signage Type")
        verbose_name_plural = _("Signage Types")
        ordering = ('label',)

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label

    def get_pictogram_url(self):
        pictogram_url = super().get_pictogram_url()
        if pictogram_url:
            return pictogram_url
        return os.path.join(settings.STATIC_URL, 'signage/picto-signage.png')


class LinePictogram(TimeStampedModelMixin, OptionalPictogramMixin):
    label = models.CharField(verbose_name=_("Label"), max_length=250, blank=True, null=False, default='')
    code = models.CharField(verbose_name=_("Code"), max_length=250, blank=True, null=False, default='')
    description = models.TextField(verbose_name=_("Description"), blank=True, help_text=_("Complete description"))

    class Meta:
        verbose_name = _("Line pictogram")
        verbose_name_plural = _("Line pictograms")

    def __str__(self):
        return self.label


class SignageCondition(TimeStampedModelMixin, StructureOrNoneRelated):
    label = models.CharField(verbose_name=_("Name"), max_length=250)

    class Meta:
        verbose_name = _("Signage Condition")
        verbose_name_plural = _("Signage Conditions")
        ordering = ["label"]

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label


class Signage(GeotrekMapEntityMixin, BaseInfrastructure):
    """ An infrastructure in the park, which is of type SIGNAGE """
    objects = SignageGISManager()
    code = models.CharField(verbose_name=_("Code"), max_length=250, blank=True, null=False, default='')
    manager = models.ForeignKey(Organism, verbose_name=_("Manager"), null=True, blank=True, on_delete=models.PROTECT)
    sealing = models.ForeignKey(Sealing, verbose_name=_("Sealing"), null=True, blank=True, on_delete=models.PROTECT)
    printed_elevation = models.IntegerField(verbose_name=_("Printed elevation"), blank=True, null=True)
    type = models.ForeignKey(SignageType, related_name='signages', verbose_name=_("Type"), on_delete=models.PROTECT)
    coordinates_verbose_name = _("Coordinates")
    conditions = models.ManyToManyField(
        SignageCondition,
        related_name='signages',
        verbose_name=_("Condition"), blank=True)

    geometry_types_allowed = ["POINT"]

    class Meta:
        verbose_name = _("Signage")
        verbose_name_plural = _("Signages")

    @classmethod
    def path_signages(cls, path):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            return cls.objects.existing().filter(aggregations__path=path).distinct('pk')
        else:
            area = path.geom.buffer(settings.TREK_SIGNAGE_INTERSECTION_MARGIN)
            return cls.objects.existing().filter(geom__intersects=area)

    @classmethod
    def topology_signages(cls, topology, queryset=None):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            qs = cls.overlapping(topology, all_objects=queryset)
        else:
            area = topology.geom.buffer(settings.TREK_SIGNAGE_INTERSECTION_MARGIN)
            qs = queryset_or_all_objects(queryset, cls)
            qs = qs.filter(geom__intersects=area)
        return qs

    @classmethod
    def published_topology_signages(cls, topology):
        return cls.topology_signages(topology).filter(published=True)

    @classmethod
    def outdoor_signages(cls, outdoor_obj, queryset=None):
        return intersecting(qs=queryset_or_model(queryset, cls), obj=outdoor_obj)

    @classmethod
    def tourism_signages(cls, tourism_obj, queryset=None):
        return intersecting(qs=queryset_or_model(queryset, cls), obj=tourism_obj)

    @property
    def order_blades(self):
        return self.blade_set.all().order_by(collate_c('number'))

    @property
    def coordinates(self):
        return "{} ({})".format(format_coordinates(self.geom), spatial_reference())

    @property
    def geomtransform(self):
        geom = self.topo_object.geom
        return geom.transform(settings.API_SRID, clone=True)

    @property
    def lat_value(self):
        return self.geomtransform.x

    @property
    def lng_value(self):
        return self.geomtransform.y

    @property
    def conditions_display(self):
        return ", ".join([str(c) for c in self.conditions.all()])

    def distance(self, to_cls):
        """Distance to associate this signage to another class"""
        return settings.TREK_SIGNAGE_INTERSECTION_MARGIN

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        for trek in self.treks.all():
            trek.save()

    def delete(self, *args, **kwargs):
        for trek in self.treks.all():
            trek.save()
        Blade.objects.filter(signage=self).update(deleted=True)
        super().delete(*args, **kwargs)


@receiver(pre_delete, sender=Topology)
def log_cascade_deletion_from_signage_topology(sender, instance, using, **kwargs):
    # Signages are deleted when Topologies (from BaseInfrastructure) are deleted
    log_cascade_deletion(sender, instance, Signage, 'topo_object')


Path.add_property('signages', lambda self: Signage.path_signages(self), _("Signages"))
Topology.add_property('signages', Signage.topology_signages, _("Signages"))
Topology.add_property('published_signages', lambda self: Signage.published_topology_signages(self),
                      _("Published Signages"))


class Direction(TimeStampedModelMixin, models.Model):
    label = models.CharField(max_length=128)

    class Meta:
        verbose_name = _("Direction")
        verbose_name_plural = _("Directions")

    def __str__(self):
        return self.label


class Color(TimeStampedModelMixin, models.Model):
    label = models.CharField(max_length=128)

    class Meta:
        verbose_name = _("Blade color")
        verbose_name_plural = _("Blade colors")

    def __str__(self):
        return self.label


class BladeType(TimeStampedModelMixin, StructureOrNoneRelated):
    """ Types of blades"""
    label = models.CharField(max_length=128)

    class Meta:
        verbose_name = _("Blade type")
        verbose_name_plural = _("Blade types")

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label


class BladeCondition(TimeStampedModelMixin, StructureOrNoneRelated):
    label = models.CharField(verbose_name=_("Name"), max_length=250)

    class Meta:
        verbose_name = _("Blade Condition")
        verbose_name_plural = _("Blade Conditions")
        ordering = ('label',)

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label


class Blade(TimeStampedModelMixin, ZoningPropertiesMixin, AddPropertyMixin, GeotrekMapEntityMixin, NoDeleteMixin):
    signage = models.ForeignKey(Signage, verbose_name=_("Signage"),
                                on_delete=models.CASCADE)
    number = models.CharField(verbose_name=_("Number"), max_length=250)
    direction = models.ForeignKey(Direction, verbose_name=_("Direction"), on_delete=models.PROTECT, null=True,
                                  blank=True)
    type = models.ForeignKey(BladeType, verbose_name=_("Type"), on_delete=models.PROTECT)
    color = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, blank=True,
                              verbose_name=_("Color"))
    # condition = models.ForeignKey(InfrastructureCondition, verbose_name=_("Condition"),
    #                               null=True, blank=True, on_delete=models.PROTECT)
    conditions = models.ManyToManyField(
        BladeCondition,
        related_name='blades',
        verbose_name=_("Condition"), blank=True)
    topology = models.ForeignKey(Topology, related_name="blades_set", verbose_name=_("Blades"), on_delete=models.CASCADE)
    colorblade_verbose_name = _("Color")
    printedelevation_verbose_name = _("Printed elevation")
    direction_verbose_name = _("Direction")
    city_verbose_name = _("City")
    bladecode_verbose_name = _("Code")
    coordinates_verbose_name = "{} ({})".format(_("Coordinates"), spatial_reference())
    can_duplicate = False

    class Meta:
        verbose_name = _("Blade")
        verbose_name_plural = _("Blades")

    @property
    def zoning_property(self):
        return self.signage

    @classproperty
    def geomfield(cls):
        return Topology._meta.get_field('geom')

    def __str__(self):
        return settings.BLADE_CODE_FORMAT.format(signagecode=self.signage.code, bladenumber=self.number)

    def set_topology(self, topology):
        self.topology = topology
        if not self.is_signage:
            raise ValueError("Expecting a signage")

    @property
    def conditions_display(self):
        return ", ".join([str(c) for c in self.conditions.all()])

    @property
    def paths(self):
        return self.signage.paths.all()

    @property
    def is_signage(self):
        if self.topology:
            return self.topology.kind == Signage.KIND
        return False

    @property
    def geom(self):
        return self.signage.geom

    @geom.setter
    def geom(self, value):
        self._geom = value

    @property
    def signage_display(self):
        return '<img src="%simages/signage-16.png" title="Signage">' % settings.STATIC_URL

    @property
    def order_lines(self):
        return self.lines.order_by('number')

    @property
    def number_display(self):
        s = '<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk, self.get_detail_url(), self, self)
        return s

    @property
    def name_display(self):
        s = '<a data-pk="%s" href="%s" title="%s">%s</a>' % (self.pk,
                                                             self.get_detail_url(),
                                                             self,
                                                             self)
        return s

    @property
    def structure(self):
        return self.signage.structure

    def same_structure(self, user):
        """ Returns True if the user is in the same structure or has
            bypass_structure permission, False otherwise. """
        return (user.profile.structure == self.structure
                or user.is_superuser
                or user.has_perm('authent.can_bypass_structure'))

    @property
    def bladecode_csv_display(self):
        return settings.BLADE_CODE_FORMAT.format(signagecode=self.signage.code,
                                                 bladenumber=self.number)

    @property
    def coordinates_csv_display(self):
        return self.coordinates or ""

    @property
    def printedelevation_csv_display(self):
        return self.signage.printed_elevation or ""

    @property
    def city_csv_display(self):
        return self.signage.cities[0] if self.signage.cities else ""

    @property
    def coordinates(self):
        return format_coordinates(self.geom)

    def distance(self, to_cls):
        """Distance to associate this blade to another class"""
        return settings.TREK_SIGNAGE_INTERSECTION_MARGIN


@receiver(pre_delete, sender=Topology)
def log_cascade_deletion_from_blade_topology(sender, instance, using, **kwargs):
    # Blade are deleted when Topology are deleted
    log_cascade_deletion(sender, instance, Blade, 'topology')


@receiver(pre_delete, sender=Signage)
def log_cascade_deletion_from_blade_signage(sender, instance, using, **kwargs):
    # Blade are deleted when Signage are deleted
    log_cascade_deletion(sender, instance, Blade, 'signage')


class Line(models.Model):
    blade = models.ForeignKey(Blade, related_name='lines', verbose_name=_("Blade"),
                              on_delete=models.CASCADE)
    number = models.IntegerField(verbose_name=_("Number"))
    direction = models.ForeignKey(Direction, verbose_name=_("Direction"), on_delete=models.PROTECT, null=True,
                                  blank=True)
    text = models.CharField(verbose_name=_("Text"), max_length=1000, blank=True, default="")
    distance = models.DecimalField(verbose_name=_("Distance"), null=True, blank=True,
                                   decimal_places=1, max_digits=8, help_text='km')
    pictograms = models.ManyToManyField('LinePictogram', related_name="lines",
                                        blank=True,
                                        verbose_name=_("Pictograms"))
    time = models.DurationField(verbose_name=pgettext_lazy("duration", "Time"), null=True, blank=True,
                                help_text=_("Hours:Minutes:Seconds"))
    distance_pretty_verbose_name = _("Distance")
    time_pretty_verbose_name = _("Time")
    linecode_verbose_name = _("Code")

    def __str__(self):
        return self.linecode

    @property
    def linecode(self):
        return settings.LINE_CODE_FORMAT.format(signagecode=self.blade.signage.code,
                                                bladenumber=self.blade.number,
                                                linenumber=self.number)

    @property
    def distance_pretty(self):
        if not self.distance:
            return ""
        return settings.LINE_DISTANCE_FORMAT.format(self.distance)

    @property
    def time_pretty(self):
        if not self.time:
            return ""
        hours = self.time.seconds // 3600
        minutes = (self.time.seconds % 3600) // 60
        seconds = self.time.seconds % 60
        return settings.LINE_TIME_FORMAT.format(hours=hours, minutes=minutes, seconds=seconds)

    class Meta:
        unique_together = (('blade', 'number'), )
        verbose_name = _("Line")
        verbose_name_plural = _("Lines")


@receiver(pre_delete, sender=Blade)
def log_cascade_deletion_from_line_blade(sender, instance, using, **kwargs):
    # Lines are deleted when Blade are deleted
    log_cascade_deletion(sender, instance, Line, 'blade')
