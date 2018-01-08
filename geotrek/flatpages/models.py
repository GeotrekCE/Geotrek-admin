import mimetypes

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings

from bs4 import BeautifulSoup
from extended_choices import Choices

from mapentity.serializers import plain_text
from geotrek.common.mixins import TimeStampedModelMixin, BasePublishableMixin


FLATPAGES_TARGETS = Choices(
    ('ALL', 'all', _('All')),
    ('MOBILE', 'mobile', _('Mobile')),
    ('HIDDEN', 'hidden', _('Hidden')),
    ('WEB', 'web', _('Web')),
)


class FlatPage(BasePublishableMixin, TimeStampedModelMixin):
    """
    Manage *Geotrek-rando* static pages from Geotrek admin.

    Historically, we started static pages as static HTML files within
    *Geotrek-rando* folders.
    """
    title = models.CharField(verbose_name=_(u'Title'), max_length=200,
                             db_column='titre')
    external_url = models.URLField(verbose_name=_(u'External URL'), blank=True,
                                   db_column='url_externe', default='',
                                   help_text=_('Link to external website instead of HTML content'))
    content = models.TextField(verbose_name=_(u'Content'), null=True, blank=True,
                               db_column='contenu',
                               help_text=_('HTML content'))
    target = models.CharField(verbose_name=_(u'Target'), max_length=12, choices=FLATPAGES_TARGETS,
                              db_column='cible', default=FLATPAGES_TARGETS.ALL)
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='flatpages',
                                    verbose_name=_("Source"), db_table='t_r_page_source')
    portal = models.ManyToManyField('common.TargetPortal',
                                    blank=True, related_name='flatpages',
                                    verbose_name=_("Portal"), db_table='t_r_page_portal')
    order = models.IntegerField(default=None, null=True, blank=True,
                                help_text=_(u"ID order if blank", ),
                                verbose_name=_(u"Order"))

    @property
    def slug(self):
        return slugify(self.title)

    class Meta:
        db_table = 'p_t_page'
        verbose_name = _(u'Flat page')
        verbose_name_plural = _(u'Flat pages')
        ordering = ['order', 'id']
        permissions = (
            ("read_flatpage", "Can read FlatPage"),
        )

    def __unicode__(self):
        return self.title

    def clean(self):
        html_content = ''
        for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            html_content += getattr(self, 'content_%s' % l[0], None) or ''

    def parse_media(self):
        soup = BeautifulSoup(self.content or '')
        images = soup.findAll('img')
        results = []
        for image in images:
            url = image.get('src')
            if url is None:
                continue

            mt = mimetypes.guess_type(url, strict=True)[0]
            if mt is None:
                mt = 'application/octet-stream'

            results.append({
                'url': url,
                'title': image.get('title', ''),
                'alt': image.get('alt', ''),
                'mimetype': mt.split('/'),
            })

        return results

    @models.permalink
    def get_add_url(self):
        return ('admin:flatpages_flatpage_add', )

    @models.permalink
    def get_update_url(self):
        return ('admin:flatpages_flatpage_change', [self.pk])

    @models.permalink
    def get_delete_url(self):
        return ('admin:flatpages_flatpage_delete', [self.pk])

    @property
    def rando_url(self):
        return 'informations/{}/'.format(self.slug)

    @property
    def meta_description(self):
        return plain_text(self.content)[:500]
