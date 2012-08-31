# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.gis.geos import GeometryCollection

from caminae.authent.models import StructureRelated
from caminae.core.models import TopologyMixin
from caminae.mapentity.models import MapEntityMixin
from caminae.common.models import Organism
from caminae.infrastructure.models import Infrastructure, Signage


class Intervention(MapEntityMixin, StructureRelated):
    in_maintenance = models.BooleanField(verbose_name=_(u"Whether the intervention is currently happening"))
    name = models.CharField(verbose_name=_(u"Name"), max_length=128)
    date = models.DateField(auto_now_add=True, verbose_name=_(u"Date"))
    comments = models.TextField(blank=True, verbose_name=_(u"Comments"))

    ## Technical information ##
    length = models.FloatField(default=0.0, verbose_name=_(u"Length"))
    width = models.FloatField(default=0.0, verbose_name=_(u"Width"))
    height = models.FloatField(default=0.0, verbose_name=_(u"Height"))
    area = models.IntegerField(default=0, verbose_name=_(u"Area"))
    slope = models.IntegerField(default=0, verbose_name=_(u"Slope"))

    ## Costs ##
    material_cost = models.FloatField(default=0.0, verbose_name=_(u"Material cost"))
    heliport_cost = models.FloatField(default=0.0, verbose_name=_(u"Heliport cost"))
    subcontract_cost = models.FloatField(default=0.0, verbose_name=_(u"Subcontract cost"))

    #TODO: remove this --> abstract class
    date_insert = models.DateTimeField(verbose_name=_(u"Insertion date"), auto_now_add=True)
    date_update = models.DateTimeField(verbose_name=_(u"Update date"), auto_now=True)
    deleted = models.BooleanField(editable=False, default=False, verbose_name=_(u"Deleted"))

    """ Topology can be of type Infrastructure or of own type Intervention """
    topology = models.ForeignKey(TopologyMixin, null=True,  #TODO: why null ?
                                 related_name="interventions",
                                 verbose_name=_(u"Interventions"))

    stake = models.ForeignKey('core.Stake', null=True,
            related_name='interventions', verbose_name=_("Stake"))

    status = models.ForeignKey('InterventionStatus', verbose_name=_("Intervention status"))

    type = models.ForeignKey('InterventionType', null=True, blank=True,
            verbose_name=_(u"Intervention type"))

    disorders = models.ManyToManyField('InterventionDisorder', related_name="interventions",
            verbose_name=_(u"Disorders"))

    jobs = models.ManyToManyField('InterventionJob', through='ManDay',
            verbose_name=_(u"Jobs"))

    project = models.ForeignKey('Project', null=True, blank=True,
            verbose_name=_(u"Project"))

    class Meta:
        db_table = 'interventions'
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
    def is_infrastructure(self):
        if self.topology:
            return self.topology.kind.pk == Infrastructure.get_kind().pk
        return False

    @property
    def is_signage(self):
        if self.topology:
            return self.topology.kind.pk == Signage.get_kind().pk
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
        if self.topology:
            if self.topology.kind.pk == Signage.get_kind().pk:
                return [Signage.objects.get(pk=self.topology.pk)]
        return []

    @property
    def infrastructures(self):
        if self.topology:
            if self.topology.kind.pk == Infrastructure.get_kind().pk:
                return [Infrastructure.objects.get(pk=self.topology.pk)]
        return []

    @property
    def geom(self):
        if self.topology:
            return self.topology.geom
        return None

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.name)

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.date)


class InterventionStatus(StructureRelated):

    status = models.CharField(verbose_name=_(u"Status"), max_length=128)

    class Meta:
        db_table = 'bib_de_suivi'
        verbose_name = _(u"Intervention's status")
        verbose_name_plural = _(u"Intervention's statuses")
        ordering = ['id']

    def __unicode__(self):
        return self.status


class InterventionType(StructureRelated):

    type = models.CharField(max_length=128, verbose_name=_(u"Type"))

    class Meta:
        db_table = 'typologie_des_interventions'
        verbose_name = _(u"Intervention's type")
        verbose_name_plural = _(u"Intervention's types")

    def __unicode__(self):
        return self.type


class InterventionDisorder(StructureRelated):

    disorder = models.CharField(max_length=128, verbose_name=_(u"Disorder"))

    class Meta:
        db_table = 'desordres'
        verbose_name = _(u"Intervention's disorder")
        verbose_name_plural = _(u"Intervention's disorders")

    def __unicode__(self):
        return self.disorder


class InterventionJob(StructureRelated):

    job = models.CharField(max_length=128, verbose_name=_(u"Job"))

    class Meta:
        db_table = 'bib_fonctions'
        verbose_name = _(u"Intervention's job")
        verbose_name_plural = _(u"Intervention's jobs")

    def __unicode__(self):
        return self.job


class ManDay(models.Model):

    nb_days = models.IntegerField(verbose_name=_(u"Mandays"))
    intervention = models.ForeignKey(Intervention)
    job = models.ForeignKey(InterventionJob)

    class Meta:
        db_table = 'journeeshomme'
        verbose_name = _(u"Manday")
        verbose_name_plural = _(u"Mandays")

    def __unicode__(self):
        return self.nb_days


class Project(MapEntityMixin, StructureRelated):

    name = models.CharField(verbose_name=_(u"Name"), max_length=128)
    begin_year = models.IntegerField(verbose_name=_(u"Begin year"))
    end_year = models.IntegerField(verbose_name=_(u"End year"))
    constraint = models.TextField(verbose_name=_(u"Constraint"), blank=True)
    cost = models.FloatField(verbose_name=_(u"Cost"), default=0)
    comments = models.TextField(verbose_name=_(u"Comments"), blank=True)

    date_insert = models.DateTimeField(verbose_name=_(u"Insertion date"), auto_now_add=True)
    date_update = models.DateTimeField(verbose_name=_(u"Update date"), auto_now=True)
    deleted = models.BooleanField(default=False, verbose_name=_(u"Deleted"))

    ## Relations ##
    contractors = models.ManyToManyField('Contractor', related_name="projects",
            verbose_name=_(u"Contractors"))

    project_owner = models.ForeignKey(Organism, related_name='own',
            verbose_name=_(u"Project owner"))

    project_manager = models.ForeignKey(Organism, related_name='manage',
            verbose_name=_(u"Project manager"))

    founders = models.ManyToManyField(Organism, through='Funding',
            verbose_name=_(u"Founders"))

    class Meta:
        db_table = 'chantiers'
        verbose_name = _(u"Project")
        verbose_name_plural = _(u"Projects")

    @property
    def paths(self):
        s = []
        for i in self.intervention_set.all():
            s += i.paths
        return list(set(s))

    @property
    def signages(self):
        s = []
        for i in self.intervention_set.all():
            s += i.signages
        return list(set(s))

    @property
    def infrastructures(self):
        s = []
        for i in self.intervention_set.all():
            s += i.infrastructures
        return list(set(s))

    @property
    def geom(self):
        """ Merge all interventions geometry into a collection
        """
        interventions = Intervention.objects.filter(project=self)
        geoms = [i.geom for i in interventions if i.geom is not None]
        if geoms:
            return GeometryCollection(*geoms)
        return None

    @property
    def name_display(self):
        return u'<a data-pk="%s" href="%s" >%s</a>' % (self.pk, self.get_detail_url(), self.name)

    def __unicode__(self):
        deleted_text = u"[" + _(u"Deleted") + u"]" if self.deleted else ""
        return u"%s (%s-%s) %s" % (self.name, self.begin_year, self.end_year, deleted_text)


class Contractor(StructureRelated):

    contractor = models.CharField(max_length=128, verbose_name=_(u"Contractor"))

    class Meta:
        db_table = 'prestataires'
        verbose_name = _(u"Contractor")
        verbose_name_plural = _(u"Contractors")

    def __unicode__(self):
        return self.contractor


class Funding(StructureRelated):

    amount = models.FloatField(default=0.0, verbose_name=_(u"Amount"))
    project = models.ForeignKey(Project)
    organism = models.ForeignKey(Organism)

    class Meta:
        db_table = 'financement'
        verbose_name = _(u"Funding")
        verbose_name_plural = _(u"Fundings")

    def __unicode__(self):
        return self.amount
