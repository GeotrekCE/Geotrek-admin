from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.conf import settings

from extended_choices import Choices

from geotrek.common.mixins import TimeStampedModelMixin, BasePublishableMixin


FLATPAGES_TARGETS = Choices(
    ('ALL', 'all', _('All')),
    ('MOBILE', 'mobile', _('Mobile')),
    ('HIDDEN', 'hidden', _('Hidden')),
)


class FlatPage(BasePublishableMixin, TimeStampedModelMixin):
    """
    Manage *Geotrek-rando* static pages from Geotrek admin.

    Historically, we started static pages as static HTML files within
    *Geotrek-rando* folders.
    """
    title = models.CharField(verbose_name=_(u'Title'), max_length=200,
                             db_column='titre')
    external_url = models.URLField(verbose_name=_(u'External URL'), null=True, blank=True,
                                   db_column='url_externe',
                                   help_text=_('Link to external website instead of HTML content'))
    content = models.TextField(verbose_name=_(u'Content'), null=True, blank=True,
                               db_column='contenu',
                               help_text=_('HTML content'))
    target = models.CharField(verbose_name=_(u'Target'), max_length=12, choices=FLATPAGES_TARGETS,
                              db_column='cible', default=FLATPAGES_TARGETS.ALL)

    @property
    def slug(self):
        return slugify(self.title)

    class Meta:
        db_table = 'p_t_page'
        verbose_name = _(u'Flat page')
        verbose_name_plural = _(u'Flat pages')

    def __unicode__(self):
        return self.title

    def clean(self):
        html_content = ''
        for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            html_content += getattr(self, 'content_%s' % l[0], None) or ''

        if self.external_url.strip() and strip_tags(html_content):
            raise ValidationError(_('Choose between external URL and HTML content'))
