# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _

from caminae.authent.models import StructureRelated
from caminae.core.models import MapEntityMixin, TopologyMixin
from caminae.common.models import Organism


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
    deleted = models.BooleanField(verbose_name=_(u"Deleted"))

    ## Relations ##
    topologies = models.ManyToManyField(TopologyMixin,
            related_name="interventions",
            verbose_name=_(u"Interventions"))

    stake = models.ForeignKey('core.Stake', null=True,
            related_name='interventions', verbose_name=_("Stake"))

    status = models.ForeignKey('InterventionStatus', verbose_name=_("Intervention status"))

    typology = models.ForeignKey('InterventionTypology', null=True, blank=True,
            verbose_name=_(u"Intervention typology"))

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

    def __unicode__(self):
        return u"%s (%s)" % (self.name , self.date)


class InterventionStatus(StructureRelated):

    status = models.CharField(verbose_name=_(u"Status"), max_length=128)

    class Meta:
        db_table = 'bib_de_suivi'
        verbose_name = _(u"Intervention's status")
        verbose_name_plural = _(u"Intervention's statuses")

    def __unicode__(self):
        return self.status


class InterventionTypology(StructureRelated):

    typology = models.CharField(max_length=128, verbose_name=_(u"Typology"))

    class Meta:
        db_table = 'typologie_des_interventions'
        verbose_name = _(u"Intervention's typology")
        verbose_name_plural = _(u"Intervention's typologies")

    def __unicode__(self):
        return self.typology


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


class Project(StructureRelated):

    project_id = models.IntegerField(primary_key=True)
    name = models.CharField(verbose_name=_(u"Name"), max_length=128)
    begin_year = models.IntegerField(verbose_name=_(u"Begin year"))
    end_year = models.IntegerField(verbose_name=_(u"End year"))
    constraint = models.TextField(verbose_name=_(u"Constraint"))
    cost = models.FloatField(verbose_name=_(u"Cost"))
    comment = models.TextField(verbose_name=_(u"Comments"))

    insert_date = models.DateTimeField(verbose_name=_(u"Insertion date"), auto_now_add=True)
    update_date = models.DateTimeField(verbose_name=_(u"Update date"), auto_now=True)

    deleted = models.BooleanField(verbose_name=_(u"Deleted"))

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

    amount = models.FloatField(verbose_name=_(u"Amount"))
    project = models.ForeignKey(Project)
    organism = models.ForeignKey(Organism)

    class Meta:
        db_table = 'financement'
        verbose_name = _(u"Funding")
        verbose_name_plural = _(u"Fundings")

    def __unicode__(self):
        return self.amount
