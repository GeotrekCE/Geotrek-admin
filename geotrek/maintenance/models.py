import os
from datetime import datetime
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models
from django.contrib.gis.geos import GeometryCollection
from django.contrib.postgres.indexes import GistIndex
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from geotrek.altimetry.models import AltimetryMixin
from geotrek.authent.models import StructureRelated, StructureOrNoneRelated
from geotrek.common.mixins.models import (TimeStampedModelMixin, NoDeleteMixin, AddPropertyMixin,
                                          GeotrekMapEntityMixin, get_uuid_duplication)
from geotrek.common.models import Organism
from geotrek.common.utils import classproperty
from geotrek.core.models import Topology, Path, Trail
from geotrek.maintenance.managers import InterventionManager, ProjectManager
from geotrek.zoning.mixins import ZoningPropertiesMixin

from mapentity.models import DuplicateMixin


if 'geotrek.signage' in settings.INSTALLED_APPS:
    from geotrek.signage.models import Blade


class Intervention(ZoningPropertiesMixin, AddPropertyMixin, GeotrekMapEntityMixin, AltimetryMixin,
                   TimeStampedModelMixin, StructureRelated, NoDeleteMixin):

    target_type = models.ForeignKey(ContentType, null=True, on_delete=models.CASCADE)
    target_id = models.PositiveIntegerField(blank=True, null=True)
    target = GenericForeignKey('target_type', 'target_id')

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

    # AltimetryMixin for denormalized fields from related topology, updated via trigger.
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

    geometry_types_allowed = ["LINESTRING", "POINT"]

    elements_duplication = {
        "attachments": {"uuid": get_uuid_duplication}
    }

    class Meta:
        verbose_name = _("Intervention")
        verbose_name_plural = _("Interventions")
        indexes = [
            GistIndex(name='intervention_geom_3d_gist_idx', fields=['geom_3d']),
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._geom = None

    def default_stake(self):
        stake = None
        if self.target and isinstance(self.target, Topology):
            for path in self.target.paths.exclude(stake=None):
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
            if isinstance(self.target, Topology):
                self.target.reload()
        return self

    def save(self, *args, **kwargs):
        if self.stake is None:
            self.stake = self.default_stake()

        super().save(*args, **kwargs)

        # Invalidate project map
        if self.project:
            try:
                os.remove(self.project.get_map_image_path())
            except OSError:
                pass

        self.reload()

    @classproperty
    def target_verbose_name(cls):
        return _("On")

    @property
    def target_display(self):
        icon = 'path'
        title = _('Paths')
        if self.target_type:
            model = self.target_type.model_class()

            if not self.target:
                title = model._meta.verbose_name + f' {self.target_id}'
                return '<i>' + _('Deleted') + ' :</i><img src="%simages/%s-16.png"> <i>%s<i/>' % (settings.STATIC_URL, icon, title)
            if not model._meta.model_name == "topology":
                title = self.target.name_display
                icon = model._meta.model_name
            return '<img src="%simages/%s-16.png"> %s' % (settings.STATIC_URL,
                                                          icon,
                                                          title)
        return '-'

    @property
    def target_csv_display(self):
        if self.target_type:
            model = self.target_type.model_class()
            if not self.target:
                title = model._meta.verbose_name + f' {self.target_id}'
                return _('Deleted') + title
            if model._meta.model_name == "topology":
                title = _('Path')
                return ", ".join(["%s: %s (%s)" % (title, path, path.pk) for path in self.target.paths.all()])
            return "%s: %s (%s)" % (
                _(self.target._meta.verbose_name),
                self.target,
                self.target.pk)
        return '-'

    @property
    def in_project(self):
        return self.project is not None

    @property
    def paths(self):
        if self.target_type:
            model = self.target_type.model_class()
            if model._meta.model_name == 'blade':
                return self.target.signage.paths.all()
            if self.target and hasattr(self.target, 'paths'):
                return self.target.paths.all()
        return Path.objects.none()

    @property
    def trails(self):
        s = []
        if hasattr(self.target, 'paths'):
            for p in self.target.paths.all():
                for t in p.trails.all():
                    s.append(t.pk)

        return Trail.objects.filter(pk__in=s)

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
            (self.material_cost or 0) + \
            (self.heliport_cost or 0) + \
            (self.subcontract_cost or 0)

    @classproperty
    def total_cost_verbose_name(cls):
        return _("Total cost")

    @classproperty
    def geomfield(cls):
        return Topology._meta.get_field('geom')

    @property
    def geom(self):
        if self._geom is None:
            if self.target:
                self._geom = self.target.geom
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
    def get_interventions(cls, obj):
        blade_content_type = ContentType.objects.get_for_model(Blade)
        non_topology_content_types = [blade_content_type]
        if 'geotrek.outdoor' in settings.INSTALLED_APPS:
            non_topology_content_types += [
                ContentType.objects.get_by_natural_key('outdoor', 'site'),
                ContentType.objects.get_by_natural_key('outdoor', 'course'),
            ]
        if settings.TREKKING_TOPOLOGY_ENABLED:
            topologies = list(Topology.overlapping(obj).values_list('pk', flat=True))
        else:
            area = obj.geom.buffer(settings.INTERVENTION_INTERSECTION_MARGIN)
            topologies = list(Topology.objects.existing().filter(geom__intersects=area).values_list('pk', flat=True))
        qs = Q(target_id__in=topologies) & ~Q(target_type__in=non_topology_content_types)
        if 'geotrek.signage' in settings.INSTALLED_APPS:
            blades = list(Blade.objects.filter(signage__in=topologies).values_list('id', flat=True))
            qs |= Q(target_id__in=blades, target_type=blade_content_type)
        return Intervention.objects.existing().filter(qs).distinct('pk')

    @classmethod
    def path_interventions(cls, path):
        blade_content_type = ContentType.objects.get_for_model(Blade)
        non_topology_content_types = [blade_content_type]
        if 'geotrek.outdoor' in settings.INSTALLED_APPS:
            non_topology_content_types += [
                ContentType.objects.get_by_natural_key('outdoor', 'site'),
                ContentType.objects.get_by_natural_key('outdoor', 'course'),
            ]
        topologies = list(Topology.objects.filter(aggregations__path=path).values_list('pk', flat=True))
        qs = Q(target_id__in=topologies) & ~Q(target_type__in=non_topology_content_types)
        if 'geotrek.signage' in settings.INSTALLED_APPS:
            blades = list(Blade.objects.filter(signage__in=topologies).values_list('id', flat=True))
            qs |= Q(target_id__in=blades, target_type=blade_content_type)
        return Intervention.objects.existing().filter(qs).distinct('pk')

    @classmethod
    def topology_interventions(cls, topology):
        return cls.get_interventions(topology)

    @classmethod
    def blade_interventions(cls, blade):
        return cls.get_interventions(blade.signage)

    @property
    def signages(self):
        if hasattr(self.target, 'signages'):
            return self.target.signages
        return []

    @property
    def infrastructures(self):
        if hasattr(self.target, 'infrastructures'):
            return self.target.infrastructures
        return []

    def distance(self, to_cls):
        """Distance to associate this intervention to another class"""
        return settings.MAINTENANCE_INTERSECTION_MARGIN

    @property
    def disorders_display(self):
        return ', '.join([str(disorder) for disorder in self.disorders.all()])

    @property
    def jobs_display(self):
        return ', '.join([str(job) for job in self.jobs.all()])


Path.add_property('interventions', lambda self: Intervention.path_interventions(self), _("Interventions"))
Topology.add_property('interventions', lambda self: Intervention.topology_interventions(self), _("Interventions"))
if 'geotrek.signage' in settings.INSTALLED_APPS:
    Blade.add_property('interventions', lambda self: Intervention.blade_interventions(self), _("Interventions"))


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
    active = models.BooleanField(verbose_name=_("Active"), default=True)

    class Meta:
        verbose_name = _("Intervention's job")
        verbose_name_plural = _("Intervention's jobs")
        ordering = ['job']

    def __str__(self):
        if self.structure:
            return "{} ({})".format(self.job, self.structure.name)
        return self.job


class ManDay(DuplicateMixin, models.Model):

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


class Project(ZoningPropertiesMixin, AddPropertyMixin, GeotrekMapEntityMixin, TimeStampedModelMixin,
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

    elements_duplication = {
        "attachments": {"uuid": get_uuid_duplication}
    }

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        ordering = ['-begin_year', 'name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._geom = None

    @property
    def paths(self):
        s = []
        for i in self.interventions.existing():
            if hasattr(i, 'paths'):
                s += i.paths
        return Path.objects.filter(pk__in=[p.pk for p in set(s)])

    @property
    def trails(self):
        s = []
        for i in self.interventions.existing():
            if i.target and hasattr(i.target, 'paths'):
                for p in i.target.paths.all():
                    for t in p.trails.all():
                        s.append(t.pk)

        return Trail.objects.filter(pk__in=s)

    @property
    def signages(self):
        from geotrek.signage.models import Signage
        target_ids = self.interventions.existing().filter(target_type=ContentType.objects.get_for_model(Signage)).values_list('target_id', flat=True)
        return list(Signage.objects.filter(topo_object__in=target_ids))

    @property
    def infrastructures(self):
        from geotrek.infrastructure.models import Infrastructure
        target_ids = list(self.interventions.existing().filter(target_type=ContentType.objects.get_for_model(Infrastructure)).values_list('target_id', flat=True))
        return list(Infrastructure.objects.filter(topo_object__in=target_ids))

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
            geoms = []
            for i in interventions:
                geom = i.geom
                if geom is not None:
                    if isinstance(geom, GeometryCollection):
                        for sub_geom in geom:
                            geoms.append(sub_geom)
                    else:
                        geoms.append(geom)
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
        return cls.objects.existing().filter(interventions__in=path.interventions.all()).distinct()

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


class Funding(DuplicateMixin, models.Model):

    amount = models.FloatField(verbose_name=_("Amount"))
    project = models.ForeignKey(Project, verbose_name=_("Project"), on_delete=models.CASCADE)
    organism = models.ForeignKey(Organism, verbose_name=_("Organism"), on_delete=models.CASCADE)

    class Meta:
        verbose_name = _("Funding")
        verbose_name_plural = _("Fundings")

    def __str__(self):
        return "%s : %s" % (self.project, self.amount)
