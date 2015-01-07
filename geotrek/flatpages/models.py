import mimetypes

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.html import strip_tags
from django.template.defaultfilters import slugify
from django.core.exceptions import ValidationError
from django.conf import settings

from bs4 import BeautifulSoup
from extended_choices import Choices

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

    @property
    def slug(self):
        return slugify(self.title)

    class Meta:
        db_table = 'p_t_page'
        verbose_name = _(u'Flat page')
        verbose_name_plural = _(u'Flat pages')
        permissions = (
            ("read_flatpage", "Can read FlatPage"),
        )

    def __unicode__(self):
        return self.title

    def clean(self):
        html_content = ''
        for l in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            html_content += getattr(self, 'content_%s' % l[0], None) or ''

        # Test if HTML was filled
        # Use strip_tags() to catch empty tags (e.g. ``<p></p>``)
        if self.external_url and self.external_url.strip() and strip_tags(html_content):
            raise ValidationError(_('Choose between external URL and HTML content'))

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
