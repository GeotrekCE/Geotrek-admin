# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.db import models
from django.contrib.gis.geos import GeometryCollection

from caminae.authent.models import StructureRelated
from caminae.core.models import NoDeleteMixin, Topology, Path, Trail
from caminae.mapentity.models import MapEntityMixin
from caminae.common.models import Organism
from caminae.common.utils import classproperty
from caminae.infrastructure.models import Infrastructure, Signage


class Intervention(MapEntityMixin, StructureRelated, NoDeleteMixin):

    in_maintenance = models.BooleanField(verbose_name=_(u"Recurrent intervention"),
                                         db_column='maintenance', help_text=_(u"Recurrent"))
    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom',
                            help_text=_(u"Brief summary"))
    date = models.DateField(default=datetime.now, verbose_name=_(u"Date"), db_column='date',
                            help_text=_(u"When ?"))
    comments = models.TextField(blank=True, verbose_name=_(u"Comments"), db_column='commentaire',
                                help_text=_(u"Remarks and notes"))

    ## Technical information ##
    width = models.FloatField(default=0.0, verbose_name=_(u"Width"), db_column='largeur')
    height = models.FloatField(default=0.0, verbose_name=_(u"Height"), db_column='hauteur')
    area = models.IntegerField(default=0, verbose_name=_(u"Area"), db_column='surface')

    # Denormalized fields from related topology. Updated via trigger.
    slope = models.FloatField(default=0.0, verbose_name=_(u"Slope"), db_column='pente')
    length = models.FloatField(default=0.0, verbose_name=_(u"Length"), db_column='longueur')
    ascent = models.IntegerField(editable=False, default=0, db_column='denivelee_positive', verbose_name=_(u"Ascent"))
    descent = models.IntegerField(editable=False, default=0, db_column='denivelee_negative', verbose_name=_(u"Descent"))
    min_elevation = models.IntegerField(editable=False, default=0, db_column='altitude_minimum', verbose_name=_(u"Minimum elevation"))
    max_elevation = models.IntegerField(editable=False, default=0, db_column='altitude_maximum', verbose_name=_(u"Maximum elevation"))

    ## Costs ##
    material_cost = models.FloatField(default=0.0, verbose_name=_(u"Material cost"), db_column='cout_materiel')
    heliport_cost = models.FloatField(default=0.0, verbose_name=_(u"Heliport cost"), db_column='cout_heliport')
    subcontract_cost = models.FloatField(default=0.0, verbose_name=_(u"Subcontract cost"), db_column='cout_soustraitant')

    #TODO: remove this --> abstract class
    date_insert = models.DateTimeField(verbose_name=_(u"Insertion date"), auto_now_add=True, db_column='date_insert')
    date_update = models.DateTimeField(verbose_name=_(u"Update date"), auto_now=True, db_column='date_update')

    """ Topology can be of type Infrastructure or of own type Intervention """
    topology = models.ForeignKey(Topology, null=True,  #TODO: why null ?
                                 related_name="interventions",
                                 verbose_name=_(u"Interventions"))

    stake = models.ForeignKey('core.Stake', null=True,
            related_name='interventions', verbose_name=_("Stake"), db_column='enjeu')

    status = models.ForeignKey('InterventionStatus', verbose_name=_("Status"), db_column='status')

    type = models.ForeignKey('InterventionType', null=True, blank=True,
            verbose_name=_(u"Type"), db_column='type')

    disorders = models.ManyToManyField('InterventionDisorder', related_name="interventions",
            db_table="m_r_intervention_desordre", verbose_name=_(u"Disorders"))

    jobs = models.ManyToManyField('InterventionJob', through='ManDay',
            verbose_name=_(u"Jobs"))

    project = models.ForeignKey('Project', null=True, blank=True, related_name="interventions",
            verbose_name=_(u"Project"), db_column='chantier')

    # Special manager
    objects = Topology.get_manager_cls()()

    class Meta:
        db_table = 'm_t_intervention'
        verbose_name = _(u"Intervention")
        verbose_name_plural = _(u"Interventions")

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

    def save(self, *args, **kwargs):
        if self.stake is None:
            self.stake = self.default_stake()
        super(Intervention, self).save(*args, **kwargs)

    @property
    def on_infrastructure(self):
        return self.is_infrastructure or self.is_signage

    @property
    def infrastructure(self):
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
        if self.on_infrastructure:
            return '<img src="%simages/%s-16.png" title="%s">' % (
                    settings.STATIC_URL,
                    self.topology.kind.lower(),
                    unicode(_(self.topology.kind)))
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
            total += md.nb_days
        return total

    @property
    def total_cost(self):
        total = 0.0
        for md in self.manday_set.all():
            total += md.cost
        return total

    @classproperty
    def geomfield(cls):
        return Topology._meta.get_field('geom')

    @property
    def geom(self):
        if self.topology:
            return self.topology.geom
        return None

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.name)

    @property
    def name_csv_display(self):
        return unicode(self.name)

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.date)

    @classmethod
    def path_interventions(cls, path):
        return Intervention.objects.filter(topology__aggregations__path=path)

    @classmethod
    def trail_interventions(cls, trail):
        """ Interventions of a trail is the union of interventions on all its paths """
        return Intervention.objects.filter(topology__aggregations__path__trail=trail)

    @classmethod
    def topology_interventions(cls, topology):
        return cls.objects.filter(aggregations__path__in=topology.paths.all()).distinct('pk')

Path.add_property('interventions', lambda self: Intervention.path_interventions(self))
Trail.add_property('interventions', lambda self: Intervention.trail_interventions(self))


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

    def __unicode__(self):
        return self.type


class InterventionDisorder(StructureRelated):

    disorder = models.CharField(max_length=128, verbose_name=_(u"Disorder"), db_column='desordre')

    class Meta:
        db_table = 'm_b_desordre'
        verbose_name = _(u"Intervention's disorder")
        verbose_name_plural = _(u"Intervention's disorders")

    def __unicode__(self):
        return self.disorder


class InterventionJob(StructureRelated):

    job = models.CharField(max_length=128, verbose_name=_(u"Job"), db_column='fonction')
    cost = models.DecimalField(verbose_name=_(u"Cost"), default=1.0, decimal_places=2, max_digits=8, db_column="cout_jour")

    class Meta:
        db_table = 'm_b_fonction'
        verbose_name = _(u"Intervention's job")
        verbose_name_plural = _(u"Intervention's jobs")

    def __unicode__(self):
        return self.job


class ManDay(models.Model):

    nb_days = models.DecimalField(verbose_name=_(u"Mandays"), decimal_places=2, max_digits=6, db_column='nb_jours')
    intervention = models.ForeignKey(Intervention, db_column='intervention')
    job = models.ForeignKey(InterventionJob, db_column='fonction')

    class Meta:
        db_table = 'm_r_intervention_fonction'
        verbose_name = _(u"Manday")
        verbose_name_plural = _(u"Mandays")

    @property
    def cost(self):
        return float(self.nb_days * self.job.cost)

    def __unicode__(self):
        return self.nb_days


class Project(MapEntityMixin, StructureRelated, NoDeleteMixin):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128, db_column='nom')
    begin_year = models.IntegerField(verbose_name=_(u"Begin year"), db_column='annee_debut')
    end_year = models.IntegerField(verbose_name=_(u"End year"), db_column='annee_fin')
    constraint = models.TextField(verbose_name=_(u"Constraint"), blank=True, db_column='contraintes',
                                  help_text=_(u"Specific conditions, ..."))
    cost = models.FloatField(verbose_name=_(u"Cost"), default=0, db_column='cout',
                             help_text=_(u"€"))
    comments = models.TextField(verbose_name=_(u"Comments"), blank=True, db_column='commentaires',
                                help_text=_(u"Remarks and notes"))
    type = models.ForeignKey('ProjectType', null=True, blank=True,
                             verbose_name=_(u"Project type"), db_column='type')
    domain = models.ForeignKey('ProjectDomain', null=True, blank=True,
                             verbose_name=_(u"Project domain"), db_column='domaine')


    date_insert = models.DateTimeField(verbose_name=_(u"Insertion date"), auto_now_add=True, db_column='date_insert')
    date_update = models.DateTimeField(verbose_name=_(u"Update date"), auto_now=True, db_column='date_update')

    ## Relations ##
    contractors = models.ManyToManyField('Contractor', related_name="projects",
            db_table="m_r_chantier_prestataire", verbose_name=_(u"Contractors"))

    project_owner = models.ForeignKey(Organism, related_name='own',
            verbose_name=_(u"Project owner"), db_column='maitre_oeuvre')

    project_manager = models.ForeignKey(Organism, related_name='manage',
            verbose_name=_(u"Project manager"), db_column='maitre_ouvrage')

    founders = models.ManyToManyField(Organism, through='Funding',
            verbose_name=_(u"Founders"))

    # Special manager
    objects = Topology.get_manager_cls()()

    class Meta:
        db_table = 'm_t_chantier'
        verbose_name = _(u"Project")
        verbose_name_plural = _(u"Projects")

    def __init__(self, *args, **kwargs):
        super(Project, self).__init__(*args, **kwargs)
        self._geom = None

    @property
    def paths(self):
        s = []
        for i in self.interventions.all():
            s += i.paths
        return Path.objects.filter(pk__in=[p.pk for p in set(s)])

    @property
    def trails(self):
        s = []
        for i in self.interventions.all():
            for p in i.paths.all():
                if p.trail:
                    s.append(p.trail)
        return Trail.objects.filter(pk__in=[t.pk for t in set(s)])

    @property
    def signages(self):
        s = []
        for i in self.interventions.all():
            s += i.signages
        return list(set(s))

    @property
    def infrastructures(self):
        s = []
        for i in self.interventions.all():
            s += i.infrastructures
        return list(set(s))

    @classproperty
    def geomfield(cls):
        from django.contrib.gis.geos import LineString
        # Fake field, TODO: still better than overkill code in views, but can do neater.
        c = GeometryCollection([LineString((0,0), (1,1))], srid=settings.SRID)
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
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.name)

    @property
    def name_csv_display(self):
        return unicode(self.name)

    @property
    def period(self):
        return "%s - %s" % (self.begin_year, self.end_year)

    @property
    def period_display(self):
        return self.period

    @classproperty
    def period_verbose_name(cls):
        return _("Period")

    def __unicode__(self):
        deleted_text = u"[" + _(u"Deleted") + u"]" if self.deleted else ""
        return u"%s (%s-%s) %s" % (self.name, self.begin_year, self.end_year, deleted_text)

    @classmethod
    def path_projects(cls, path):
        return cls.objects.filter(interventions__in=path.interventions)

    @classmethod
    def trail_projects(cls, trail):
        return cls.objects.filter(interventions__in=trail.interventions)

    @classmethod
    def topology_projects(cls, topology):
        return cls.objects.filter(interventions__in=topology.interventions)

    def edges_by_attr(self, interventionattr):
        pks = []
        for i in self.interventions.all():
            pks += getattr(i, interventionattr).values_list('pk', flat=True)
        return Topology.objects.filter(pk__in=pks)

Path.add_property('projects', lambda self: Project.path_projects(self))
Topology.add_property('projects', lambda self: Project.topology_projects(self))
Trail.add_property('projects', lambda self: Project.trail_projects(self))


class ProjectType(StructureRelated):

    type = models.CharField(max_length=128, verbose_name=_(u"Type"), db_column='type')

    class Meta:
        db_table = 'm_b_chantier'
        verbose_name = _(u"Project type")
        verbose_name_plural = _(u"Project types")

    def __unicode__(self):
        return self.type


class ProjectDomain(StructureRelated):

    domain = models.CharField(max_length=128, verbose_name=_(u"Domain"), db_column='domaine')

    class Meta:
        db_table = 'm_b_domaine'
        verbose_name = _(u"Project domain")
        verbose_name_plural = _(u"Project domains")

    def __unicode__(self):
        return self.domain


class Contractor(StructureRelated):

    contractor = models.CharField(max_length=128, verbose_name=_(u"Contractor"), db_column='prestataire')

    class Meta:
        db_table = 'm_b_prestataire'
        verbose_name = _(u"Contractor")
        verbose_name_plural = _(u"Contractors")

    def __unicode__(self):
        return self.contractor


class Funding(models.Model):

    amount = models.FloatField(default=0.0, verbose_name=_(u"Amount"), db_column='montant')
    project = models.ForeignKey(Project, db_column='chantier')
    organism = models.ForeignKey(Organism, db_column='organisme')

    class Meta:
        db_table = 'm_r_chantier_financement'
        verbose_name = _(u"Funding")
        verbose_name_plural = _(u"Fundings")

    def __unicode__(self):
        return self.amount
