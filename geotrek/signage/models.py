import os

from django.db import models
from django.utils.translation import ugettext_lazy as _, pgettext_lazy

from django.conf import settings

from mapentity.models import MapEntityMixin

from geotrek.authent.models import StructureOrNoneRelated, StructureRelated
from geotrek.common.mixins import AddPropertyMixin, NoDeleteMixin, OptionalPictogramMixin, NoDeleteManager
from geotrek.common.models import Organism
from geotrek.common.utils import classproperty, format_coordinates
from geotrek.core.models import Topology, Path

from geotrek.infrastructure.models import BaseInfrastructure, InfrastructureCondition


class Sealing(StructureOrNoneRelated):
    """ A sealing linked with a signage"""
    label = models.CharField(verbose_name=_("Name"), max_length=250)

    class Meta:
        verbose_name = _("Sealing")
        verbose_name_plural = _("Sealings")

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label


class SignageType(StructureOrNoneRelated, OptionalPictogramMixin):
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
        pictogram_url = super(SignageType, self).get_pictogram_url()
        if pictogram_url:
            return pictogram_url
        return os.path.join(settings.STATIC_URL, 'signage/picto-signage.png')


class SignageGISManager(NoDeleteManager):
    """ Overide default typology mixin manager, and filter by type. """
    def all_implantation_years(self):
        all_years = self.get_queryset().filter(implantation_year__isnull=False)\
            .order_by('-implantation_year').values_list('implantation_year', flat=True).distinct('implantation_year')
        return all_years


class Signage(MapEntityMixin, BaseInfrastructure):
    """ An infrastructure in the park, which is of type SIGNAGE """
    objects = SignageGISManager()
    code = models.CharField(verbose_name=_("Code"), max_length=250, blank=True, null=True)
    manager = models.ForeignKey(Organism, verbose_name=_("Manager"), null=True, blank=True, on_delete=models.CASCADE)
    sealing = models.ForeignKey(Sealing, verbose_name=_("Sealing"), null=True, blank=True, on_delete=models.CASCADE)
    printed_elevation = models.IntegerField(verbose_name=_("Printed elevation"), blank=True, null=True)
    type = models.ForeignKey(SignageType, verbose_name=_("Type"), on_delete=models.CASCADE)
    gps_value_verbose_name = _("GPS coordinates")

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
    def topology_signages(cls, topology):
        if settings.TREKKING_TOPOLOGY_ENABLED:
            qs = cls.overlapping(topology)
        else:
            area = topology.geom.buffer(settings.TREK_SIGNAGE_INTERSECTION_MARGIN)
            qs = cls.objects.existing().filter(geom__intersects=area)
        return qs

    @classmethod
    def published_topology_signages(cls, topology):
        return cls.topology_signages(topology).filter(published=True)

    @property
    def order_blades(self):
        return self.blade_set.all().order_by('number')

    @property
    def gps_value(self):
        return format_coordinates(self.topo_object.geom)

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


Path.add_property('signages', lambda self: Signage.path_signages(self), _("Signages"))
Topology.add_property('signages', Signage.topology_signages, _("Signages"))
Topology.add_property('published_signages', lambda self: Signage.published_topology_signages(self),
                      _("Published Signages"))


class Direction(models.Model):
    label = models.CharField(max_length=128)

    class Meta:
        verbose_name = _("Direction")
        verbose_name_plural = _("Directions")

    def __str__(self):
        return self.label


class Color(models.Model):
    label = models.CharField(max_length=128)

    class Meta:
        verbose_name = _("Blade color")
        verbose_name_plural = _("Blade colors")

    def __str__(self):
        return self.label


class BladeType(StructureOrNoneRelated):
    """ Types of blades"""
    label = models.CharField(max_length=128)

    class Meta:
        verbose_name = _("Blade type")
        verbose_name_plural = _("Blade types")

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.label, self.structure.name)
        return self.label


class Blade(AddPropertyMixin, MapEntityMixin):
    signage = models.ForeignKey(Signage, verbose_name=_("Signage"),
                                on_delete=models.PROTECT)
    number = models.CharField(verbose_name=_("Number"), max_length=250)
    direction = models.ForeignKey(Direction, verbose_name=_("Direction"), on_delete=models.PROTECT)
    type = models.ForeignKey(BladeType, verbose_name=_("Type"), on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.PROTECT, null=True, blank=True,
                              verbose_name=_("Color"))
    condition = models.ForeignKey(InfrastructureCondition, verbose_name=_("Condition"),
                                  null=True, blank=True, on_delete=models.PROTECT)
    topology = models.ForeignKey(Topology, related_name="blades_set", verbose_name=_("Blades"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Blade")
        verbose_name_plural = _("Blades")

    def __str__(self):
        return settings.BLADE_CODE_FORMAT.format(signagecode=self.signage.code, bladenumber=self.number)

    def set_topology(self, topology):
        self.topology = topology
        if not self.is_signage:
            raise ValueError("Expecting a signage")

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
        return self.topology.geom

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


class Line(models.Model):
    blade = models.ForeignKey(Blade, related_name='lines', verbose_name=_("Blade"),
                              on_delete=models.CASCADE)
    number = models.IntegerField(verbose_name=_("Number"))
    text = models.CharField(verbose_name=_("Text"), max_length=1000)
    distance = models.DecimalField(verbose_name=_("Distance"), null=True, blank=True,
                                   decimal_places=3, max_digits=8)
    pictogram_name = models.CharField(verbose_name=_("Pictogramm name"), max_length=250,
                                      blank=True, null=True)
    time = models.DurationField(verbose_name=pgettext_lazy("duration", "Time"), null=True, blank=True,
                                help_text=_("Hours:Minutes:Seconds"))
    distance_verbose_name = _("Distance (km)")
    time_verbose_name = _("Time (Hours:Minutes:Seconds)")
    colorblade_verbose_name = _("Color")
    linecode_verbose_name = _("Code")
    printedelevation_verbose_name = _("Printed elevation")
    direction_verbose_name = _("Direction")

    @classproperty
    def geomfield(cls):
        return Topology._meta.get_field('geom')

    def __str__(self):
        return self.linecode_csv_display

    @property
    def linecode_csv_display(self):
        return settings.LINE_CODE_FORMAT.format(signagecode=self.blade.signage.code,
                                                bladenumber=self.blade.number,
                                                linenumber=self.number)

    @property
    def colorblade_csv_display(self):
        return self.blade.color or ""

    @property
    def signage_csv_display(self):
        return "%s #%s" % (self.blade.signage, self.blade.number)

    @property
    def lat_csv_display(self):
        return self.blade.signage.lat_value

    @property
    def lng_csv_display(self):
        return self.blade.signage.lng_value

    @property
    def printedelevation_csv_display(self):
        return self.blade.signage.printed_elevation or ""

    @property
    def direction_csv_display(self):
        return self.blade.direction or ""

    @property
    def geom(self):
        return self.blade.geom

    @property
    def structure(self):
        return self.blade.signage.structure

    class Meta:
        unique_together = (('blade', 'number'), )
        verbose_name = _("Line")
        verbose_name_plural = _("Lines")
