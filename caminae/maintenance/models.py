# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _

from caminae.authent.models import StructureRelated


class Intervention(models.Model):

    # idintervention serial
    intervention_id = models.IntegerField(primary_key=True)

    # Entretien courant BOO(32)
    in_maintenance = models.BooleanField(verbose_name=_(u"Whether the intervention is currently happening"))

    # nom intervention AV(128)
    name = models.CharField(verbose_name=_(u"Name"), max_length=128)

    # date intervention D(8)
    date = models.DateField(verbose_name=_(u"Date"))

    # remarques TXT(1000)
    comment = models.TextField(verbose_name=_(u"Comments"))

    ## Technical information ##
    # longueur saisie DEC(10,2)
    length = models.FloatField(verbose_name=_(u"Length"))
    # largeur DEC(10,2)
    width = models.FloatField(verbose_name=_(u"Width"))
    # Hauteur DEC(2,1)
    height = models.FloatField(verbose_name=_(u"Height"))
    # surface NS(2)
    area = models.IntegerField(verbose_name=_(u"Area"))
    # pente NS(2)
    slope = models.IntegerField(verbose_name=_(u"Slope"))

    ## Suivi_ des coûts A(15) ##
    # coût materiel NR(5,2)
    material_cost = models.FloatField(verbose_name=_(u"Material cost"))
    # cout héliportage NR(5,2)
    heliport_cost = models.FloatField(verbose_name=_(u"Heliport cost"))
    # cout sous-traitance NR(5,2)
    subcontract_cost = models.FloatField(verbose_name=_(u"Subcontract cost"))

    # date_insert DH(12)
    insert_date = models.DateTimeField(verbose_name=_(u"Insertion date"), auto_now_add=True)

    # date_update DH(12)
    update_date = models.DateTimeField(verbose_name=_(u"Update date"), auto_now=True)

    # Supprime BOO(1)
    deleted = models.BooleanField(verbose_name=_(u"Deleted"))

    #
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

    code = models.IntegerField(primary_key=True)
    status = models.CharField(verbose_name=_(u"Status"), max_length=128)

    class Meta:
        db_table = 'bib_de_suivi'
        verbose_name = _(u"Intervention's status")
        verbose_name_plural = _(u"Intervention's statuses")

    def __unicode__(self):
        return self.status


class InterventionTypology(StructureRelated):

    code = models.IntegerField(primary_key=True)
    typology = models.CharField(max_length=128, verbose_name=_(u"Typology"))

    class Meta:
        db_table = 'typologie_des_interventions'
        verbose_name = _(u"Intervention's typology")
        verbose_name_plural = _(u"Intervention's typologies")

    def __unicode__(self):
        return self.typology


class InterventionDisorder(StructureRelated):

    code = models.IntegerField(primary_key=True)
    disorder = models.CharField(max_length=128, verbose_name=_(u"Disorder"))

    class Meta:
        db_table = 'desordres'
        verbose_name = _(u"Intervention's disorder")
        verbose_name_plural = _(u"Intervention's disorders")

    def __unicode__(self):
        return self.disorder

class InterventionJob(StructureRelated):

    code = models.IntegerField(primary_key=True)
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


class Project(models.Model):

    # idchantier serial
    project_id = models.IntegerField(primary_key=True)

    # Nom du chantier AV(128)
    name = models.CharField(verbose_name=_(u"Name"), max_length=128)

    # année debut NS(2)
    begin_year = models.IntegerField(verbose_name=_(u"Begin year"))

    # année fin NS(2)
    end_year = models.IntegerField(verbose_name=_(u"End year"))

    # contraintes TXT(1000)
    constraint = models.TextField(verbose_name=_(u"Constraint"))

    # Coût du chantier DEC(10,2)
    cost = models.FloatField(verbose_name=_(u"Cost"))

    # remarques TXT(1000)
    comment = models.TextField(verbose_name=_(u"Comments"))

    # date_insert DH(12)
    insert_date = models.DateTimeField(verbose_name=_(u"Insertion date"), auto_now_add=True)

    # date_update DH(12)
    update_date = models.DateTimeField(verbose_name=_(u"Update date"), auto_now=True)

    # Supprime BOO(1)
    deleted = models.BooleanField(verbose_name=_(u"Deleted"))

    contractors = models.ManyToManyField('Contractor', related_name="projects",
            verbose_name=_(u"Contractors"))

    # Maître ouvrage
    project_owner = models.ForeignKey('Organism', related_name='own',
            verbose_name=_(u"Project owner"))

    # Maître d'oeuvre
    project_manager = models.ForeignKey('Organism', related_name='manage',
            verbose_name=_(u"Project manager"))

    founders = models.ManyToManyField('Organism', through='Funding',
            verbose_name=_(u"Founders"))

    class Meta:
        db_table = 'chantiers'
        verbose_name = _(u"Project")
        verbose_name_plural = _(u"Projects")

    def __unicode__(self):
        deleted_txt = u"[" + _(u"Deleted") + u"]" if self.deleted else ""
        return u"%s (%s-%s) %s" % (self.name, self.begin_year, self.end_year, deleted_text)


class Contractor(StructureRelated):

    code = models.IntegerField(primary_key=True)
    contractor = models.CharField(max_length=128, verbose_name=_(u"Contractor"))

    class Meta:
        db_table = 'prestataires'
        verbose_name = _(u"Contractor")
        verbose_name_plural = _(u"Contractors")

    def __unicode__(self):
        return self.contractor


class Organism(models.Model):

    code = models.IntegerField(primary_key=True)
    organism = models.CharField(max_length=128, verbose_name=_(u"Organism"))

    class Meta:
        db_table = 'liste_de_tous_les_organismes'
        verbose_name = _(u"Organism")
        verbose_name_plural = _(u"Organisms")

    def __unicode__(self):
        return self.organism


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

