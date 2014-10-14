from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from extended_choices import Choices

from geotrek.common.mixins import TimeStampedModelMixin, BasePublishableMixin


FLATPAGES_TARGETS = Choices(
    ('ALL', 'all', _("All")),
    ('MOBILE', 'mobile', _("Mobile")),
    ('HIDDEN', 'hidden', _("Hidden")),
)


class FlatPage(BasePublishableMixin, TimeStampedModelMixin):
    title = models.CharField(verbose_name=_(u'Title'), max_length=200,
                             db_column="titre")
    content = models.TextField(verbose_name=_(u'Content'), blank=True,
                               db_column="contenu")
    target = models.CharField(verbose_name=_(u'Target'), max_length=12, choices=FLATPAGES_TARGETS,
                              db_column="cible", default=FLATPAGES_TARGETS.ALL)

    @property
    def slug(self):
        return slugify(self.title)

    class Meta:
        db_table = 'p_t_page'
        verbose_name = _(u'Flat page')
        verbose_name_plural = _(u'Flat pages')

    def __unicode__(self):
        return self.title
