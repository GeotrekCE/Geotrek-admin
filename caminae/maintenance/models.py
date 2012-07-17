# -*- coding: utf-8 -*-


from django.db import models
from django.utils.translation import ugettext_lazy as _

from caminae.auth.models import StructureRelated


class Intervention(models.Model):

    # idintervention serial
    intervention_id = models.IntegerField(primary_key=True)

    # Entretien courant BOO(32)
    in_maintenance = models.BooleanField(verbose_name=_(u"Whether the intervention is currently happening"))

    # nom intervention AV(128)
    name = models.CharField(max_length=128)

    # date intervention D(8)
    date = models.DateField()

    # remarques TXT(1000)
    comment = models.TextField()

    ## Technical information ##
    # longueur saisie DEC(10,2)
    length = models.FloatField()
    # largeur DEC(10,2)
    width = models.FloatField()
    # Hauteur DEC(2,1)
    height = models.FloatField()
    # surface NS(2)
    area = models.IntegerField()
    # pente NS(2)
    slope = models.IntegerField()

    ## Suivi_ des coûts A(15) ##
    # coût materiel NR(5,2)
    material_cost = models.FloatField()
    # cout héliportage NR(5,2)
    heliport_cost = models.FloatField()
    # cout sous-traitance NR(5,2)
    subcontract_cost = models.FloatField()

    # date_insert DH(12)
    insert_date = models.DateTimeField(auto_now_add=True)

    # date_update DH(12)
    update_date = models.DateTimeField(auto_now=True)

    # Supprime BOO(1)
    deleted = models.BooleanField()

    #
    status = models.ForeignKey('InterventionStatus', verbose_name=_("Intervention status"))

    typology = models.ForeignKey('InterventionTypology', null=True, blank=True,
            verbose_name=_(u"Intervention typology"))

    disorders = models.ManyToManyField('InterventionDisorder',
            related_name="interventions", verbose_name=_(u"Disorders"))

    jobs = models.ManyToManyField('InterventionJob', through='ManDay')

    project = models.ForeignKey('Project', null=True, blank=True)

    class Meta:
        db_table = 'interventions'


class InterventionStatus(StructureRelated):

    code = models.IntegerField()
    status = models.TextField(max_length=128)

    class Meta:
        db_table = 'bib_de_suivi'


class InterventionTypology(StructureRelated):

    code = models.IntegerField(primary_key=True)
    typology = models.TextField(max_length=128)

    class Meta:
        db_table = 'typologie_des_interventions'


class InterventionDisorder(StructureRelated):

    code = models.IntegerField(primary_key=True)
    disorder = models.TextField(max_length=128)

    class Meta:
        db_table = 'desordres'


class InterventionJob(StructureRelated):

    code = models.IntegerField(primary_key=True)
    job = models.TextField(max_length=128)

    class Meta:
        db_table = 'bib_fonctions'


class ManDay(models.Model):

    nb_days = models.IntegerField()
    intervention = models.ForeignKey(Intervention)
    job = models.ForeignKey(InterventionJob)

    class Meta:
        db_table = 'journeeshomme'


class Project(models.Model):

    # idchantier serial
    project_id = models.IntegerField(primary_key=True)

    # Nom du chantier AV(128)
    name = models.CharField(max_length=128)

    # année debut NS(2)
    begin_year = models.IntegerField()

    # année fin NS(2)
    end_year = models.IntegerField()

    # contraintes TXT(1000)
    constraint = models.TextField()

    # Coût du chantier DEC(10,2)
    cost = models.FloatField()

    # remarques TXT(1000)
    comment = models.TextField()

    # date_insert DH(12)
    insert_date = models.DateTimeField(auto_now_add=True)

    # date_update DH(12)
    update_date = models.DateTimeField(auto_now=True)

    # Supprime BOO(1)
    deleted = models.BooleanField()

    contractors = models.ManyToManyField('Contractor',
            related_name="projects", verbose_name=_(u"Contractors"))

    # Maître ouvrage
    project_owner = models.ForeignKey('Organism', related_name='own')

    # Maître d'oeuvre
    project_manager = models.ForeignKey('Organism', related_name='manage')

    founders = models.ManyToManyField('Organism', through='Funding')

    class Meta:
        db_table = 'chantiers'


class Contractor(StructureRelated):

    code = models.IntegerField(primary_key=True)
    contractor = models.TextField(max_length=128)

    class Meta:
        db_table = 'prestataires'


class Organism(models.Model):

    code = models.IntegerField(primary_key=True)
    organism = models.TextField(max_length=128)

    class Meta:
        db_table = 'liste_de_tous_les_organismes'


class Funding(StructureRelated):

    amount = models.FloatField()
    project = models.ForeignKey(Project)
    organism = models.ForeignKey(Organism)

    class Meta:
        db_table = 'financement'


