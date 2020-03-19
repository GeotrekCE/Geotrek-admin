import os
from datetime import datetime

from django.db.models.functions import ExtractYear
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.contrib.gis.geos import GeometryCollection

from mapentity.models import MapEntityMixin

from geotrek.authent.models import StructureRelated, StructureOrNoneRelated
from geotrek.altimetry.models import AltimetryMixin
from geotrek.core.models import Topology, Path, Trail
from geotrek.common.models import Organism
from geotrek.common.mixins import TimeStampedModelMixin, NoDeleteMixin, AddPropertyMixin, NoDeleteManager
from geotrek.common.utils import classproperty


if 'geotrek.signage' in settings.INSTALLED_APPS:
    from geotrek.signage.models import Blade


class InterventionManager(NoDeleteManager):
    def all_years(self):
        return self.existing().filter(date__isnull=False).annotate(year=ExtractYear('date')) \
            .order_by('-year').values_list('year', flat=True).distinct()


class Intervention(AddPropertyMixin, MapEntityMixin, AltimetryMixin,
                   TimeStampedModelMixin, StructureRelated, NoDeleteMixin):

    content_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    name = models.CharField(verbose_name=_("Name"), max_length=128, help_text=_("Brief summary"))
    date = models.DateField(default=datetime.now, verbose_name=_("Date"), help_text=_("When ?"))
    subcontracting = models.BooleanField(verbose_name=_("Subcontracting"), default=False)

    # Technical information
    width = models.FloatField(default=0.0, blank=True, null=True, verbose_name=_("Width"))
    height = models.FloatField(default=0.0, blank=True, null=True, verbose_name=_("Height"))
    area = models.FloatField(editable=False, default=0, blank=True, null=True, verbose_name=_("Area"))

    # Costs
    material_cost = models.FloatField(default=0.0, blank=True, null=True, verbose_name=_("Material cost"))
    heliport_cost = models.FloatField(default=0.0, blank=True, null=True, verbose_name=_("Heliport cost"))
    subcontract_cost = models.FloatField(default=0.0, blank=True, null=True, verbose_name=_("Subcontract cost"))

    # AltimetyMixin for denormalized fields from related topology, updated via trigger.
    length = models.FloatField(editable=True, default=0.0, null=True, blank=True, verbose_name=_("3D Length"))

    stake = models.ForeignKey('core.Stake', null=True, blank=True, on_delete=models.CASCADE,
                              related_name='interventions', verbose_name=_("Stake"))

    status = models.ForeignKey('InterventionStatus', verbose_name=_("Status"), on_delete=models.CASCADE)

    type = models.ForeignKey('InterventionType', null=True, blank=True, on_delete=models.CASCADE,
                             verbose_name=_("Type"))

    disorders = models.ManyToManyField('InterventionDisorder', related_name="interventions",
                                       verbose_name=_("Disorders"), blank=True)

    jobs = models.ManyToManyField('InterventionJob', through='ManDay', verbose_name=_("Jobs"))

    project = models.ForeignKey('Project', null=True, blank=True, related_name="interventions",
                                on_delete=models.CASCADE, verbose_name=_("Project"))
    description = models.TextField(blank=True, verbose_name=_("Description"), help_text=_("Remarks and notes"))

    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)

    objects = InterventionManager()

    class Meta:
        verbose_name = _("Intervention")
        verbose_name_plural = _("Interventions")

    def __init__(self, *args, **kwargs):
        super(Intervention, self).__init__(*args, **kwargs)
        self._geom = None

    def default_stake(self):
        stake = None
        if self.content_object:
            for path in self.content_object.paths.exclude(stake=None):
                if path.stake > stake:
                    stake = path.stake
        return stake

    def reload(self):
        if self.pk:
            fromdb = self.__class__.objects.get(pk=self.pk)
            self.area = fromdb.area
            AltimetryMixin.reload(self, fromdb)
            TimeStampedModelMixin.reload(self, fromdb)
            NoDeleteMixin.reload(self, fromdb)
            if isinstance(self.content_object, Topology):
                self.content_object.reload()
        return self

    def save(self, *args, **kwargs):
        if self.stake is None:
            self.stake = self.default_stake()

        super(Intervention, self).save(*args, **kwargs)

        # Set kind of Intervention topology
        if self.content_object and not self.on_existing_target:
            topology_kind = self._meta.object_name.upper()
            self.content_object.kind = topology_kind
            self.content_object.save(update_fields=['kind'])

        # Invalidate project map
        if self.project:
            try:
                os.remove(self.project.get_map_image_path())
            except OSError:
                pass

        self.reload()

    @property
    def on_existing_target(self):
        return bool(self.content_object)

    @classproperty
    def related_object(cls):
        return ""

    @classproperty
    def related_object_verbose_name(cls):
        return _("On")

    @property
    def object_picture(self):
        if self.content_object._meta.model_name == "topology":
            return "images/path-16.png"
        return "images/%s-16.png" % self.content_object._meta.model_name

    @property
    def related_object_display(self):
        icon = 'path'
        title = _('Paths')
        if not self.content_object._meta.model_name == "topology":
            icon = self.content_object._meta.model_name

            title = self.content_object.name_display
        return '<img src="%simages/%s-16.png"> %s' % (settings.STATIC_URL,
                                                      icon,
                                                      title)

    @property
    def related_object_csv_display(self):
        if self.on_existing_target:
            return "%s: %s (%s)" % (
                _(self.content_object.kind.capitalize()),
                self.content_object,
                self.content_object.pk)
        return ''

    @property
    def in_project(self):
        return self.project is not None

    @property
    def on_blade(self):
        return self.content_object._meta.model_name == 'blade'

    @property
    def paths(self):
        if self.on_blade:
            return self.content_object.signage.paths.all()
        if self.content_object:
            return self.content_object.paths.all()
        return Path.objects.none()

    @property
    def total_manday(self):
        total = 0.0
        for md in self.manday_set.all():
            total += float(md.nb_days)
        return total

    @classproperty
    def total_manday_verbose_name(cls):
        return _("Mandays")

    @property
    def total_cost_mandays(self):
        total = 0.0
        for md in self.manday_set.all():
            total += md.cost
        return total

    @classproperty
    def total_cost_mandays_verbose_name(cls):
        return _("Mandays cost")

    @property
    def total_cost(self):
        return self.total_cost_mandays + \
            self.material_cost or 0 + \
            self.heliport_cost or 0 + \
            self.subcontract_cost or 0

    @classproperty
    def total_cost_verbose_name(cls):
        return _("Total cost")

    @classproperty
    def geomfield(cls):
        return Topology._meta.get_field('geom')

    @property
    def geom(self):
        if self._geom is None:
            if self.content_object:
                self._geom = self.content_object.geom
        return self._geom

    @geom.setter
    def geom(self, value):
        self._geom = value

    @property
    def api_geom(self):
        if not self.geom:
            return None
        return self.geom.transform(settings.API_SRID, clone=True)

    @property
    def name_display(self):
        return '<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk,
                                                                 self.get_detail_url(),
                                                                 self.name,
                                                                 self.name)

    @property
    def name_csv_display(self):
        return self.name

    def __str__(self):
        return "%s (%s)" % (self.name, self.date)

    @classmethod
    def path_interventions(cls, path):
        topologies = list(Topology.objects.filter(aggregations__path=path).values_list('pk', flat=True))
        if 'geotrek.signage' in settings.INSTALLED_APPS:
            topologies.extend(
                Blade.objects.filter(signage__in=topologies).values_list('pk', flat=True)
            )
        return cls.objects.existing().filter(object_id__in=topologies)

    @classmethod
    def topology_interventions(cls, topology):
        topologies = list(Topology.overlapping(topology).values_list('pk', flat=True))
        if 'geotrek.signage' in settings.INSTALLED_APPS:
            topologies.extend(
                Blade.objects.filter(signage__in=topologies).values_list('id', flat=True)
            )
        return cls.objects.existing().filter(object_id__in=topologies).distinct('pk')

    @property
    def signages(self):
        if self.content_type == ContentType.objects.get(model='signage'):
            return [self.content_object]
        return []

    @property
    def infrastructures(self):
        if self.content_type == ContentType.objects.get(model='infrastructure'):
            return [self.content_object]
        return []


Path.add_property('interventions', lambda self: Intervention.path_interventions(self), _("Interventions"))
Topology.add_property('interventions', lambda self: Intervention.topology_interventions(self), _("Interventions"))


class InterventionStatus(StructureOrNoneRelated):

    status = models.CharField(verbose_name=_("Status"), max_length=128)
    order = models.PositiveSmallIntegerField(default=None, null=True, blank=True, verbose_name=_("Display order"))

    class Meta:
        verbose_name = _("Intervention's status")
        verbose_name_plural = _("Intervention's statuses")
        ordering = ['order', 'status']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.status, self.structure.name)
        return self.status


class InterventionType(StructureOrNoneRelated):

    type = models.CharField(max_length=128, verbose_name=_("Type"))

    class Meta:
        verbose_name = _("Intervention's type")
        verbose_name_plural = _("Intervention's types")
        ordering = ['type']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.type, self.structure.name)
        return self.type


class InterventionDisorder(StructureOrNoneRelated):

    disorder = models.CharField(max_length=128, verbose_name=_("Disorder"))

    class Meta:
        verbose_name = _("Intervention's disorder")
        verbose_name_plural = _("Intervention's disorders")
        ordering = ['disorder']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.disorder, self.structure.name)
        return self.disorder


class InterventionJob(StructureOrNoneRelated):

    job = models.CharField(max_length=128, verbose_name=_("Job"))
    cost = models.DecimalField(verbose_name=_("Cost"), default=1.0, decimal_places=2, max_digits=8)

    class Meta:
        verbose_name = _("Intervention's job")
        verbose_name_plural = _("Intervention's jobs")
        ordering = ['job']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.job, self.structure.name)
        return self.job


class ManDay(models.Model):

    nb_days = models.DecimalField(verbose_name=_("Mandays"), decimal_places=2, max_digits=6)
    intervention = models.ForeignKey(Intervention, on_delete=models.CASCADE)
    job = models.ForeignKey(InterventionJob, verbose_name=_("Job"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Manday")
        verbose_name_plural = _("Mandays")

    @property
    def cost(self):
        return float(self.nb_days * self.job.cost)

    def __str__(self):
        return str(self.nb_days)


class ProjectManager(NoDeleteManager):
    def all_years(self):
        all_years = list(self.existing().exclude(begin_year=None).values_list('begin_year', flat=True))
        all_years += list(self.existing().exclude(end_year=None).values_list('end_year', flat=True))
        all_years.sort(reverse=True)
        return all_years


class Project(AddPropertyMixin, MapEntityMixin, TimeStampedModelMixin,
              StructureRelated, NoDeleteMixin):

    name = models.CharField(verbose_name=_("Name"), max_length=128)
    begin_year = models.IntegerField(verbose_name=_("Begin year"))
    end_year = models.IntegerField(verbose_name=_("End year"), blank=True, null=True)
    constraint = models.TextField(verbose_name=_("Constraint"), blank=True,
                                  help_text=_("Specific conditions, ..."))
    global_cost = models.FloatField(verbose_name=_("Global cost"), default=0,
                                    blank=True, null=True, help_text=_("€"))
    comments = models.TextField(verbose_name=_("Comments"), blank=True,
                                help_text=_("Remarks and notes"))
    type = models.ForeignKey('ProjectType', null=True, blank=True, on_delete=models.CASCADE,
                             verbose_name=_("Type"))
    domain = models.ForeignKey('ProjectDomain', null=True, blank=True, on_delete=models.CASCADE,
                               verbose_name=_("Domain"))
    contractors = models.ManyToManyField('Contractor', related_name="projects", blank=True,
                                         verbose_name=_("Contractors"))
    project_owner = models.ForeignKey(Organism, related_name='own', blank=True, null=True, on_delete=models.CASCADE,
                                      verbose_name=_("Project owner"))
    project_manager = models.ForeignKey(Organism, related_name='manage', blank=True, null=True, on_delete=models.CASCADE,
                                        verbose_name=_("Project manager"))
    founders = models.ManyToManyField(Organism, through='Funding', verbose_name=_("Founders"))
    eid = models.CharField(verbose_name=_("External id"), max_length=1024, blank=True, null=True)

    objects = ProjectManager()

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-begin_year', 'name']

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self._geom = None

    @property
    def paths(self):
        s = []
        for i in self.interventions.existing():
            s += i.paths
        return Path.objects.filter(pk__in=[p.pk for p in set(s)])

    @property
    def trails(self):
        s = []
        for i in self.interventions.existing():
            for p in i.content_object.paths.all():
                for t in p.trails.all():
                    s.append(t.pk)

        return Trail.objects.filter(pk__in=s)

    @property
    def signages(self):
        from geotrek.signage.models import Signage
        object_ids = self.interventions.existing().filter(content_type=ContentType.objects.get(model='signage')).values_list('object_id', flat=True)
        return list(Signage.objects.filter(topo_object__in=object_ids))

    @property
    def infrastructures(self):
        from geotrek.infrastructure.models import Infrastructure
        object_ids = list(self.interventions.existing().filter(content_type=ContentType.objects.get(model='infrastructure')).values_list('object_id', flat=True))
        return list(Infrastructure.objects.filter(topo_object__in=object_ids))

    @classproperty
    def geomfield(cls):
        from django.contrib.gis.geos import LineString
        # Fake field, TODO: still better than overkill code in views, but can do neater.
        c = GeometryCollection([LineString((0, 0), (1, 1))], srid=settings.SRID)
        c.name = 'geom'
        return c

    @property
    def geom(self):
        """ Merge all interventions geometry into a collection
        """
        if self._geom is None:
            interventions = Intervention.objects.existing().filter(project=self)
            geoms = [i.geom for i in interventions if i.geom is not None]
            if geoms:
                self._geom = GeometryCollection(*geoms, srid=settings.SRID)
        return self._geom

    @property
    def api_geom(self):
        if not self.geom:
            return None
        return self.geom.transform(settings.API_SRID, clone=True)

    @geom.setter
    def geom(self, value):
        self._geom = value

    @property
    def name_display(self):
        return '<a data-pk="%s" href="%s" title="%s">%s</a>' % (self.pk,
                                                                self.get_detail_url(),
                                                                self.name,
                                                                self.name)

    @property
    def name_csv_display(self):
        return self.name

    @property
    def interventions_csv_display(self):
        return [str(i) for i in self.interventions.existing()]

    @property
    def contractors_display(self):
        return [str(c) for c in self.contractors.all()]

    @property
    def founders_display(self):
        return [str(f) for f in self.founders.all()]

    @property
    def period(self):
        return "%s - %s" % (self.begin_year, self.end_year or "")

    @property
    def period_display(self):
        return self.period

    @classproperty
    def period_verbose_name(cls):
        return _("Period")

    @property
    def interventions_total_cost(self):
        total = 0
        qs = self.interventions.existing()
        for i in qs.prefetch_related('manday_set', 'manday_set__job'):
            total += i.total_cost
        return total

    @classproperty
    def interventions_total_cost_verbose_name(cls):
        return _("Interventions total cost")

    def __str__(self):
        return "%s - %s" % (self.begin_year, self.name)

    @classmethod
    def path_projects(cls, path):
        return cls.objects.existing().filter(interventions__in=path.interventions).distinct()

    @classmethod
    def topology_projects(cls, topology):
        return cls.objects.existing().filter(interventions__in=topology.interventions.all()).distinct()

    def edges_by_attr(self, interventionattr):
        """ Return related topology objects of project, by aggregating the same attribute
        on its interventions.
        (See geotrek.land.models)
        """
        pks = []
        modelclass = Topology
        for i in self.interventions.all():
            attr_value = getattr(i, interventionattr)
            if isinstance(attr_value, list):
                pks += [o.pk for o in attr_value]
            else:
                modelclass = attr_value.model
                topologies = attr_value.values('id')
                for topology in topologies:
                    pks.append(topology['id'])
        return modelclass.objects.filter(pk__in=pks)

    @classmethod
    def get_create_label(cls):
        return _("Add a new project")


Path.add_property('projects', lambda self: Project.path_projects(self), _("Projects"))
Topology.add_property('projects', lambda self: Project.topology_projects(self), _("Projects"))


class ProjectType(StructureOrNoneRelated):

    type = models.CharField(max_length=128, verbose_name=_("Type"))

    class Meta:
        verbose_name = _("Project type")
        verbose_name_plural = _("Project types")
        ordering = ['type']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.type, self.structure.name)
        return self.type


class ProjectDomain(StructureOrNoneRelated):

    domain = models.CharField(max_length=128, verbose_name=_("Domain"))

    class Meta:
        verbose_name = _("Project domain")
        verbose_name_plural = _("Project domains")
        ordering = ['domain']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.domain, self.structure.name)
        return self.domain


class Contractor(StructureOrNoneRelated):

    contractor = models.CharField(max_length=128, verbose_name=_("Contractor"))

    class Meta:
        verbose_name = _("Contractor")
        verbose_name_plural = _("Contractors")
        ordering = ['contractor']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.contractor, self.structure.name)
        return self.contractor


class Funding(models.Model):

    amount = models.FloatField(verbose_name=_("Amount"))
    project = models.ForeignKey(Project, verbose_name=_("Project"), on_delete=models.CASCADE)
    organism = models.ForeignKey(Organism, verbose_name=_("Organism"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Funding")
        verbose_name_plural = _("Fundings")

    def __str__(self):
        return "%s : %s" % (self.project, self.amount)


if 'geotrek.core' in settings.INSTALLED_APPS:
    from geotrek.core.models import Topology
    Topology.add_property('intervention', lambda self: Intervention.objects.filter(
        content_type=ContentType.objects.get(app_label='core',
                                             model='topology'),
        object_id=self.pk), verbose_name=_("Intervention"))

if 'geotrek.signage' in settings.INSTALLED_APPS:
    from geotrek.signage.models import Blade
    Blade.add_property('intervention', lambda self: Intervention.objects.filter(
        content_type=ContentType.objects.get(app_label='signage',
                                             model='blade'),
        object_id=self.pk), verbose_name=_("Intervention"))
