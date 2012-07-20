from django.contrib.gis.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from caminae.authent.models import StructureRelated
from caminae.maintenance.models import Intervention


# GeoDjango note:
# Django automatically creates indexes on geometry fields but it uses a
# syntax which is not compatible with PostGIS 2.0. That's why index creation
# is explicitly disbaled here (see manual index creation in custom SQL files).


class Path(StructureRelated):
    geom = models.LineStringField(srid=settings.SRID, spatial_index=False)
    geom_cadastre = models.LineStringField(null=True, srid=settings.SRID,
                                           spatial_index=False)
    date_insert = models.DateField(auto_now_add=True, verbose_name=_(u"Insertion date"))
    date_update = models.DateField(auto_now=True, verbose_name=_(u"Update date"))
    valid = models.BooleanField(db_column='troncon_valide', default=True, verbose_name=_(u"Validity"))
    name = models.CharField(null=True, max_length=20, db_column='nom_troncon', verbose_name=_(u"Name"))
    comments = models.TextField(null=True, db_column='remarques', verbose_name=_(u"Comments"))

    # Override default manager
    objects = models.GeoManager()

    # Computed values (managed at DB-level with triggers)
    length = models.IntegerField(editable=False, default=0, db_column='longueur', verbose_name=_(u"Length"))
    ascent = models.IntegerField(
            editable=False, default=0, db_column='denivelee_positive', verbose_name=_(u"Ascent"))
    descent = models.IntegerField(
            editable=False, default=0, db_column='denivelee_negative', verbose_name=_(u"Descent"))
    min_elevation = models.IntegerField(
            editable=False, default=0, db_column='altitude_minimum', verbose_name=_(u"Minimum elevation"))
    max_elevation = models.IntegerField(
            editable=False, default=0, db_column='altitude_maximum', verbose_name=_(u"Maximum elevation"))

    def __unicode__(self):
        return self.name

    class Meta:
        db_table = 'troncons'
        verbose_name = _(u"Path")
        verbose_name_plural = _(u"Paths")


class TopologyMixin(models.Model):
    date_insert = models.DateField(auto_now_add=True, verbose_name=_(u"Insertion date"))
    date_update = models.DateField(auto_now=True, verbose_name=_(u"Update date"))
    troncons = models.ManyToManyField(Path, through='PathAggregation', verbose_name=_(u"Path"))
    offset = models.IntegerField(db_column='decallage', verbose_name=_(u"Offset"))
    deleted = models.BooleanField(db_column='supprime', verbose_name=_(u"Deleted"))

    # Override default manager
    objects = models.GeoManager()

    # Computed values (managed at DB-level with triggers)
    length = models.FloatField(editable=False, db_column='longueur', verbose_name=_(u"Length"))
    geom = models.LineStringField(
            editable=False, srid=settings.SRID, spatial_index=False)

    kind = models.ForeignKey('TopologyMixinKind', verbose_name=_(u"Kind"))

    interventions = models.ManyToManyField(Intervention, verbose_name=_(u"Interventions"))

    def __unicode__(self):
        return u"%s (%s)" % (_(u"Topology"), self.pk)

    class Meta:
        db_table = 'evenements'
        verbose_name = _(u"Topology")
        verbose_name_plural = _(u"Topologies")


class TopologyMixinKind(models.Model):

    code = models.IntegerField(primary_key=True)
    kind = models.CharField(max_length=128, verbose_name=_(u"Topology's kind"))

    def __unicode__(self):
        return self.kind

    class Meta:
        db_table = 'type_evenements'
        verbose_name = _(u"Topology's kind")
        verbose_name_plural = _(u"Topology's kinds")


class PathAggregation(models.Model):
    path = models.ForeignKey(Path, null=False, db_column='troncon', verbose_name=_(u"Path"))
    topo_object = models.ForeignKey(TopologyMixin, null=False,
                                    db_column='evenement', verbose_name=_(u"Topology"))
    start_position = models.FloatField(db_column='pk_debut', verbose_name=_(u"Start position"))
    end_position = models.FloatField(db_column='pk_fin', verbose_name=_(u"End position"))

    # Override default manager
    objects = models.GeoManager()

    def __unicode__(self):
        return u"%s (%s - %s)" % (_("Path aggregation"), self.start_position, self.end_position)

    class Meta:
        db_table = 'evenements_troncons'
        verbose_name = _(u"Path aggregation")
        verbose_name_plural = _(u"Path aggregations")

