import mimetypes

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings
from django.urls import reverse

from bs4 import BeautifulSoup
from extended_choices import Choices

from mapentity.serializers import plain_text
from geotrek.common.mixins.models import TimeStampedModelMixin, BasePublishableMixin


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
    title = models.CharField(verbose_name=_('Title'), max_length=200)
    external_url = models.URLField(verbose_name=_('External URL'), blank=True, default='',
                                   help_text=_('Link to external website instead of HTML content'))
    content = models.TextField(verbose_name=_('Content'), null=True, blank=True,
                               help_text=_('HTML content'))
    target = models.CharField(verbose_name=_('Target'), max_length=12, choices=FLATPAGES_TARGETS,
                              default=FLATPAGES_TARGETS.ALL)
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='flatpages',
                                    verbose_name=_("Source"))
    portal = models.ManyToManyField('common.TargetPortal',
                                    blank=True, related_name='flatpages',
                                    verbose_name=_("Portal"))
    order = models.IntegerField(default=None, null=True, blank=True,
                                help_text=_("ID order if blank", ),
                                verbose_name=_("Order"))
    attachments = GenericRelation(settings.PAPERCLIP_ATTACHMENT_MODEL)

    @property
    def slug(self):
        return slugify(self.title)

    class Meta:
        verbose_name = _('Flat page')
        verbose_name_plural = _('Flat pages')
        ordering = ['order', 'id']
        permissions = (
            ("read_flatpage", "Can read FlatPage"),
        )

    def __str__(self):
        return self.title

    def get_permission_codename(self, *args):
        return

    def clean(self):
        html_content = ''
        for language in settings.MAPENTITY_CONFIG['TRANSLATED_LANGUAGES']:
            html_content += getattr(self, 'content_%s' % language[0], None) or ''

    def parse_media(self):
        soup = BeautifulSoup(self.content or '', features='html.parser')
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

    def get_add_url(self):
        return reverse('admin:flatpages_flatpage_add')

    def get_update_url(self):
        return reverse('admin:flatpages_flatpage_change', args=[self.pk])

    def get_delete_url(self):
        return reverse('admin:flatpages_flatpage_delete', args=[self.pk])

    @property
    def rando_url(self):
        return 'informations/{}/'.format(self.slug)

    @property
    def meta_description(self):
        return plain_text(self.content)[:500]

    def is_public(self):
        return self.any_published
