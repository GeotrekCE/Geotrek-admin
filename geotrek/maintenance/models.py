# -*- coding: utf-8 -*-
import os
from datetime import datetime

from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models
from django.contrib.gis.geos import GeometryCollection

from mapentity.models import MapEntityMixin

from geotrek.authent.models import StructureRelated
from geotrek.altimetry.models import AltimetryMixin
from geotrek.core.models import Topology, Path, Trail
from geotrek.common.models import Organism
from geotrek.common.mixins import TimeStampedModelMixin, NoDeleteMixin, AddPropertyMixin
from geotrek.common.utils import classproperty
from geotrek.infrastructure.models import Infrastructure, Signage


class InterventionManager(models.GeoManager):
    def all_years(self):
        all_dates = self.existing().values_list('date', flat=True)
        all_years = list(reversed(sorted(set([d.year for d in all_dates]))))
        return all_years


class Intervention(AddPropertyMixin, MapEntityMixin, AltimetryMixin,
                   TimeStampedModelMixin, StructureRelated, NoDeleteMixin):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom',
                            help_text=_(u"Brief summary"))
    date = models.DateField(default=datetime.now, verbose_name=_(u"Date"), db_column='date',
                            help_text=_(u"When ?"))
    subcontracting = models.BooleanField(verbose_name=_(u"Subcontracting"), default=False,
                                         db_column='sous_traitance')

    # Technical information
    width = models.FloatField(default=0.0, verbose_name=_(u"Width"), db_column='largeur')
    height = models.FloatField(default=0.0, verbose_name=_(u"Height"), db_column='hauteur')
    area = models.FloatField(editable=False, default=0, verbose_name=_(u"Area"), db_column='surface')

    # Costs
    material_cost = models.FloatField(default=0.0, verbose_name=_(u"Material cost"), db_column='cout_materiel')
    heliport_cost = models.FloatField(default=0.0, verbose_name=_(u"Heliport cost"), db_column='cout_heliport')
    subcontract_cost = models.FloatField(default=0.0, verbose_name=_(u"Subcontract cost"), db_column='cout_soustraitant')

    """ Topology can be of type Infrastructure or of own type Intervention """
    topology = models.ForeignKey(Topology, null=True,  # TODO: why null ?
                                 related_name="interventions_set",
                                 verbose_name=_(u"Interventions"))
    # AltimetyMixin for denormalized fields from related topology, updated via trigger.

    stake = models.ForeignKey('core.Stake', null=True,
                              related_name='interventions', verbose_name=_("Stake"), db_column='enjeu')

    status = models.ForeignKey('InterventionStatus', verbose_name=_("Status"), db_column='status')

    type = models.ForeignKey('InterventionType', null=True, blank=True,
                             verbose_name=_(u"Type"), db_column='type')

    disorders = models.ManyToManyField('InterventionDisorder', related_name="interventions",
                                       db_table="m_r_intervention_desordre", verbose_name=_(u"Disorders"),
                                       blank=True)

    jobs = models.ManyToManyField('InterventionJob', through='ManDay', verbose_name=_(u"Jobs"))

    project = models.ForeignKey('Project', null=True, blank=True, related_name="interventions",
                                verbose_name=_(u"Project"), db_column='chantier')
    description = models.TextField(blank=True, verbose_name=_(u"Description"), db_column='descriptif',
                                   help_text=_(u"Remarks and notes"))

    objects = NoDeleteMixin.get_manager_cls(InterventionManager)()

    class Meta:
        db_table = 'm_t_intervention'
        verbose_name = _(u"Intervention")
        verbose_name_plural = _(u"Interventions")

    def __init__(self, *args, **kwargs):
        super(Intervention, self).__init__(*args, **kwargs)
        self._geom = None

    def set_infrastructure(self, baseinfra):
        self.topology = baseinfra
        if not self.on_infrastructure:
            raise ValueError("Expecting an infrastructure or signage")

    def default_stake(self):
        stake = None
        if self.topology:
            for path in self.topology.paths.all():
                if path.stake > stake:
                    stake = path.stake
        return stake

    def reload(self, fromdb=None):
        if self.pk:
            fromdb = self.__class__.objects.get(pk=self.pk)
            self.area = fromdb.area
            AltimetryMixin.reload(self, fromdb)
            TimeStampedModelMixin.reload(self, fromdb)
            NoDeleteMixin.reload(self, fromdb)
            if self.topology:
                self.topology.reload()
        return self

    def save(self, *args, **kwargs):
        if self.stake is None:
            self.stake = self.default_stake()

        super(Intervention, self).save(*args, **kwargs)

        # Set kind of Intervention topology
        if self.topology and not self.on_infrastructure:
            topology_kind = self._meta.object_name.upper()
            self.topology.kind = topology_kind
            self.topology.save(update_fields=['kind'])

        # Invalidate project map
        if self.project:
            try:
                os.remove(self.project.get_map_image_path())
            except OSError:
                pass

        self.reload()

    @property
    def on_infrastructure(self):
        return self.is_infrastructure or self.is_signage

    @property
    def infrastructure(self):
        """
        Equivalent of topology attribute, but casted to related type (Infrastructure or Signage)
        """
        if self.on_infrastructure:
            if self.is_signage:
                return self.signages[0]
            if self.is_infrastructure:
                return self.infrastructures[0]
        return None

    @classproperty
    def infrastructure_verbose_name(cls):
        return _("On")

    @property
    def infrastructure_display(self):
        icon = 'path'
        title = _('Path')
        if self.on_infrastructure:
            icon = self.topology.kind.lower()
            title = u'%s: %s' % (_(self.topology.kind.capitalize()),
                                 self.infrastructure)

        return u'<img src="%simages/%s-16.png" title="%s">' % (settings.STATIC_URL,
                                                               icon,
                                                               title)

    @property
    def infrastructure_csv_display(self):
        if self.on_infrastructure:
            return u"%s: %s (%s)" % (
                _(self.topology.kind.capitalize()),
                self.infrastructure,
                self.infrastructure.pk)
        return ''

    @property
    def is_infrastructure(self):
        if self.topology:
            return self.topology.kind == Infrastructure.KIND
        return False

    @property
    def is_signage(self):
        if self.topology:
            return self.topology.kind == Signage.KIND
        return False

    @property
    def in_project(self):
        return self.project is not None

    @property
    def paths(self):
        if self.topology:
            return self.topology.paths.all()
        return []

    @property
    def signages(self):
        if self.is_signage:
            return [Signage.objects.existing().get(pk=self.topology.pk)]
        return []

    @property
    def infrastructures(self):
        if self.is_infrastructure:
            return [Infrastructure.objects.existing().get(pk=self.topology.pk)]
        return []

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
            self.material_cost + \
            self.heliport_cost + \
            self.subcontract_cost

    @classproperty
    def total_cost_verbose_name(cls):
        return _("Total cost")

    @classproperty
    def geomfield(cls):
        return Topology._meta.get_field('geom')

    @property
    def geom(self):
        if self._geom is None:
            if self.topology:
                self._geom = self.topology.geom
        return self._geom

    @geom.setter
    def geom(self, value):
        self._geom = value

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" title="%s" >%s</a>' % (self.pk,
                                                                  self.get_detail_url(),
                                                                  self.name,
                                                                  self.name)

    @property
    def name_csv_display(self):
        return unicode(self.name)

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.date)

    @classmethod
    def path_interventions(cls, path):
        return cls.objects.existing().filter(topology__aggregations__path=path)

    @classmethod
    def topology_interventions(cls, topology):
        topos = Topology.overlapping(topology).values_list('pk', flat=True)
        return cls.objects.existing().filter(topology__in=topos).distinct('pk')


Path.add_property('interventions', lambda self: Intervention.path_interventions(self), _(u"Interventions"))
Topology.add_property('interventions', lambda self: Intervention.topology_interventions(self), _(u"Interventions"))


class InterventionStatus(StructureRelated):

    status = models.CharField(verbose_name=_(u"Status"), max_length=128, db_column='status')

    class Meta:
        db_table = 'm_b_suivi'
        verbose_name = _(u"Intervention's status")
        verbose_name_plural = _(u"Intervention's statuses")
        ordering = ['id']

    def __unicode__(self):
        return self.status


class InterventionType(StructureRelated):

    type = models.CharField(max_length=128, verbose_name=_(u"Type"), db_column='type')

    class Meta:
        db_table = 'm_b_intervention'
        verbose_name = _(u"Intervention's type")
        verbose_name_plural = _(u"Intervention's types")
        ordering = ['type']

    def __unicode__(self):
        return self.type


class InterventionDisorder(StructureRelated):

    disorder = models.CharField(max_length=128, verbose_name=_(u"Disorder"), db_column='desordre')

    class Meta:
        db_table = 'm_b_desordre'
        verbose_name = _(u"Intervention's disorder")
        verbose_name_plural = _(u"Intervention's disorders")
        ordering = ['disorder']

    def __unicode__(self):
        return self.disorder


class InterventionJob(StructureRelated):

    job = models.CharField(max_length=128, verbose_name=_(u"Job"), db_column='fonction')
    cost = models.DecimalField(verbose_name=_(u"Cost"), default=1.0, decimal_places=2, max_digits=8, db_column="cout_jour")

    class Meta:
        db_table = 'm_b_fonction'
        verbose_name = _(u"Intervention's job")
        verbose_name_plural = _(u"Intervention's jobs")
        ordering = ['job']

    def __unicode__(self):
        return self.job


class ManDay(models.Model):

    nb_days = models.DecimalField(verbose_name=_(u"Mandays"), decimal_places=2, max_digits=6, db_column='nb_jours')
    intervention = models.ForeignKey(Intervention, db_column='intervention')
    job = models.ForeignKey(InterventionJob, verbose_name=_(u"Job"), db_column='fonction')

    class Meta:
        db_table = 'm_r_intervention_fonction'
        verbose_name = _(u"Manday")
        verbose_name_plural = _(u"Mandays")

    @property
    def cost(self):
        return float(self.nb_days * self.job.cost)

    def __unicode__(self):
        return self.nb_days


class ProjectManager(models.GeoManager):
    def all_years(self):
        all_years = []
        for (begin, end) in self.existing().values_list('begin_year', 'end_year'):
            all_years.append(begin)
            all_years.append(end)
        all_years = list(reversed(sorted(set(all_years))))
        return all_years


class Project(AddPropertyMixin, MapEntityMixin, TimeStampedModelMixin,
              StructureRelated, NoDeleteMixin):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom')
    begin_year = models.IntegerField(verbose_name=_(u"Begin year"), db_column='annee_debut')
    end_year = models.IntegerField(verbose_name=_(u"End year"), db_column='annee_fin')
    constraint = models.TextField(verbose_name=_(u"Constraint"), blank=True, db_column='contraintes',
                                  help_text=_(u"Specific conditions, ..."))
    global_cost = models.FloatField(verbose_name=_(u"Global cost"), default=0, db_column='cout_global',
                                    help_text=_(u"€"))
    comments = models.TextField(verbose_name=_(u"Comments"), blank=True, db_column='commentaires',
                                help_text=_(u"Remarks and notes"))
    type = models.ForeignKey('ProjectType', null=True, blank=True,
                             verbose_name=_(u"Type"), db_column='type')
    domain = models.ForeignKey('ProjectDomain', null=True, blank=True,
                               verbose_name=_(u"Domain"), db_column='domaine')
    contractors = models.ManyToManyField('Contractor', related_name="projects",
                                         db_table="m_r_chantier_prestataire", verbose_name=_(u"Contractors"))
    project_owner = models.ForeignKey(Organism, related_name='own',
                                      verbose_name=_(u"Project owner"), db_column='maitre_oeuvre')
    project_manager = models.ForeignKey(Organism, related_name='manage',
                                        verbose_name=_(u"Project manager"), db_column='maitre_ouvrage')
    founders = models.ManyToManyField(Organism, through='Funding', verbose_name=_(u"Founders"))

    objects = NoDeleteMixin.get_manager_cls(ProjectManager)()

    class Meta:
        db_table = 'm_t_chantier'
        verbose_name = _(u"Project")
        verbose_name_plural = _(u"Projects")
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
            for p in i.paths.all():
                if p.trail:
                    s.append(p.trail)
        return Trail.objects.filter(pk__in=[t.pk for t in set(s)])

    @property
    def signages(self):
        s = []
        for i in self.interventions.existing():
            s += i.signages
        return list(set(s))

    @property
    def infrastructures(self):
        s = []
        for i in self.interventions.existing():
            s += i.infrastructures
        return list(set(s))

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

    @geom.setter
    def geom(self, value):
        self._geom = value

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" title="%s">%s</a>' % (self.pk,
                                                                 self.get_detail_url(),
                                                                 self.name,
                                                                 self.name)

    @property
    def name_csv_display(self):
        return unicode(self.name)

    @property
    def interventions_csv_display(self):
        return [unicode(i) for i in self.interventions.existing()]

    @property
    def period(self):
        return "%s - %s" % (self.begin_year, self.end_year)

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

    def __unicode__(self):
        return u"%s (%s-%s)" % (self.name, self.begin_year, self.end_year)

    @classmethod
    def path_projects(cls, path):
        return cls.objects.existing().filter(interventions__in=path.interventions).distinct()

    @classmethod
    def topology_projects(cls, topology):
        return cls.objects.existing().filter(interventions__in=topology.interventions).distinct()

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
                topologies = attr_value.values('ordering', 'id')
                for topology in topologies:
                    pks.append(topology['id'])
        return modelclass.objects.filter(pk__in=pks)

    @classmethod
    def get_create_label(cls):
        return _(u"Add a new project")


Path.add_property('projects', lambda self: Project.path_projects(self), _(u"Projects"))
Topology.add_property('projects', lambda self: Project.topology_projects(self), _(u"Projects"))


class ProjectType(StructureRelated):

    type = models.CharField(max_length=128, verbose_name=_(u"Type"), db_column='type')

    class Meta:
        db_table = 'm_b_chantier'
        verbose_name = _(u"Project type")
        verbose_name_plural = _(u"Project types")
        ordering = ['type']

    def __unicode__(self):
        return self.type


class ProjectDomain(StructureRelated):

    domain = models.CharField(max_length=128, verbose_name=_(u"Domain"), db_column='domaine')

    class Meta:
        db_table = 'm_b_domaine'
        verbose_name = _(u"Project domain")
        verbose_name_plural = _(u"Project domains")
        ordering = ['domain']

    def __unicode__(self):
        return self.domain


class Contractor(StructureRelated):

    contractor = models.CharField(max_length=128, verbose_name=_(u"Contractor"), db_column='prestataire')

    class Meta:
        db_table = 'm_b_prestataire'
        verbose_name = _(u"Contractor")
        verbose_name_plural = _(u"Contractors")
        ordering = ['contractor']

    def __unicode__(self):
        return self.contractor


class Funding(models.Model):

    amount = models.FloatField(default=0.0, verbose_name=_(u"Amount"), db_column='montant')
    project = models.ForeignKey(Project, verbose_name=_(u"Project"), db_column='chantier')
    organism = models.ForeignKey(Organism, verbose_name=_(u"Organism"), db_column='organisme')

    class Meta:
        db_table = 'm_r_chantier_financement'
        verbose_name = _(u"Funding")
        verbose_name_plural = _(u"Fundings")

    def __unicode__(self):
        return self.amount
