from django.db import models
from django.utils.translation import ugettext_lazy as _

from caminae.core.models import TopologyMixin
from caminae.authent.models import StructureRelated


INFRASTRUCTURE_TYPES = (
    ('A', _("Infrastructure")),
    ('E', _("Facility")),
    ('S', _("Signage")),
)


class InfrastructureType(StructureRelated):
    label = models.CharField(db_column="nom", max_length=128)
    type = models.CharField(db_column="type", max_length=1, choices=INFRASTRUCTURE_TYPES)

    class Meta:
        db_table = 'classe_amenagement'
        verbose_name = _(u"Infrastructure Type")
        verbose_name_plural = _(u"Infrastructure Types")

    def __unicode__(self):
        return self.label


class Infrastructure(TopologyMixin, StructureRelated):
    name = models.CharField(db_column="nom", max_length=128)
    description = models.TextField(blank=True)
    type = models.ForeignKey(InfrastructureType)

    class Meta:
        db_table = 'amenagement'
        verbose_name = _(u"Infrastructure")
        verbose_name_plural = _(u"Infrastructure")

    def __unicode__(self):
        return self.name
