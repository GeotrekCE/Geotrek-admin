import mimetypes

from django.contrib.contenttypes.fields import GenericRelation
from django.contrib import admin
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify
from django.conf import settings
from django.urls import reverse

from bs4 import BeautifulSoup
from extended_choices import Choices
from treebeard.mp_tree import MP_Node

from mapentity.serializers import plain_text
from geotrek.common.mixins.models import (
    TimeStampedModelMixin, BasePublishableMixin, OptionalPictogramMixin
)

FLATPAGES_TARGETS = Choices(
    ('ALL', 'all', _('All')),
    ('MOBILE', 'mobile', _('Mobile')),
    ('HIDDEN', 'hidden', _('Hidden')),
    ('WEB', 'web', _('Web')),
)


class FlatPage(BasePublishableMixin, TimeStampedModelMixin, MP_Node):
    """
    Manage *Geotrek-rando* static pages from Geotrek admin.

    Historically, we started static pages as static HTML files within
    *Geotrek-rando* folders.
    """
    title = models.CharField(verbose_name=_('Title'), max_length=200)
    content = models.TextField(verbose_name=_('Content'), null=True, blank=True,
                               help_text=_('HTML content'))
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='flatpages',
                                    verbose_name=_("Source"))
    portals = models.ManyToManyField('common.TargetPortal',
                                     blank=True, related_name='flatpages',
                                     verbose_name=_("Portal"))
    attachments = GenericRelation(settings.PAPERCLIP_ATTACHMENT_MODEL)

    @property
    def slug(self):
        return slugify(self.title)

    class Meta:
        verbose_name = _('Flat page')
        verbose_name_plural = _('Flat pages')
        ordering = ['id']
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
        soup = BeautifulSoup(self.content or '', 'lxml')
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

    @admin.display(description='Portals')
    def portal_names_string(self):
        return ", ".join(p.name for p in self.portals.all())


class MenuItem(OptionalPictogramMixin, BasePublishableMixin, TimeStampedModelMixin, MP_Node):

    TARGET_TYPE_CHOICES = (
        ("Page", "page"),
        ("Link", "link"),
    )

    PLATFORM_CHOICES = Choices(
        ('ALL', 'all', _('All')),
        ('MOBILE', 'mobile', _('Mobile')),
        ('WEB', 'web', _('Web')),
    )

    label = models.CharField(verbose_name=_('Label'), max_length=50)
    target_type = models.CharField(max_length=10, null=True, choices=TARGET_TYPE_CHOICES)
    link_url = models.URLField(verbose_name=_('Link URL'), blank=True, default='')
    page = models.ForeignKey(FlatPage, on_delete=models.SET_NULL, null=True, blank=True)
    platform = models.CharField(verbose_name=_('Platform'), max_length=12, choices=PLATFORM_CHOICES,
                                default=PLATFORM_CHOICES.ALL)
    portals = models.ManyToManyField('common.TargetPortal',
                                     blank=True, related_name='menu_items',
                                     verbose_name=_("Portal"))
    open_in_new_tab = models.BooleanField(verbose_name=_('Open the link in a new tab'), default=False)
    attachments = GenericRelation(settings.PAPERCLIP_ATTACHMENT_MODEL)

    class Meta:
        verbose_name = _('Menu item')
        verbose_name_plural = _('Menu items')

    @property
    def slug(self):
        return slugify(self.label)

    def __str__(self):
        return self.label

    def get_add_url(self):
        return reverse('admin:flatpages_menuitem_add')

    def get_update_url(self):
        return reverse('admin:flatpages_menuitem_change', args=[self.pk])

    def get_delete_url(self):
        return reverse('admin:flatpages_menuitem_delete', args=[self.pk])

    @admin.display(description='Portals')
    def portal_names_string(self):
        return ", ".join(p.name for p in self.portals.all())
