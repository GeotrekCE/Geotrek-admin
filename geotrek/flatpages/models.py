from extended_choices import Choices

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.translation import gettext_lazy as _
from geotrek.common.mixins.models import (
    TimeStampedModelMixin, BasePublishableMixin, OptionalPictogramMixin
)
from treebeard.mp_tree import MP_Node


class FlatPage(BasePublishableMixin, TimeStampedModelMixin, MP_Node):

    title = models.CharField(verbose_name=_('Title'), max_length=200)
    content = models.TextField(verbose_name=_('Content'), null=True, blank=True,
                               help_text=_('HTML content'))
    source = models.ManyToManyField('common.RecordSource',
                                    blank=True, related_name='flatpages',
                                    verbose_name=_("Source"))
    portals = models.ManyToManyField('common.TargetPortal',
                                     blank=True, related_name='flatpages',
                                     verbose_name=_("Portals"))
    attachments = GenericRelation(settings.PAPERCLIP_ATTACHMENT_MODEL)

    class Meta:
        verbose_name = _('Flat page')
        verbose_name_plural = _('Flat pages')
        permissions = (
            ("read_flatpage", "Can read FlatPage"),
        )

    def __str__(self):
        return self.title


class MenuItem(OptionalPictogramMixin, BasePublishableMixin, TimeStampedModelMixin, MP_Node):

    TARGET_TYPE_CHOICES = Choices(
        ("PAGE", "page", _("Page")),
        ("LINK", "link", _("Link")),
    )

    PLATFORM_CHOICES = Choices(
        ('ALL', 'all', _('All')),
        ('MOBILE', 'mobile', _('Mobile')),
        ('WEB', 'web', _('Web')),
    )

    title = models.CharField(verbose_name=_('Title'), max_length=200)
    target_type = models.CharField(max_length=10, verbose_name=_('Target type'), null=True, blank=True, choices=TARGET_TYPE_CHOICES)
    link_url = models.CharField(max_length=200, verbose_name=_('Link URL'), blank=True, default='')
    page = models.ForeignKey(FlatPage, on_delete=models.SET_NULL, null=True, blank=True, related_name="menu_items")
    platform = models.CharField(verbose_name=_('Platform'), max_length=12, choices=PLATFORM_CHOICES,
                                default=PLATFORM_CHOICES.ALL)
    portals = models.ManyToManyField('common.TargetPortal',
                                     blank=True, related_name='menu_items',
                                     verbose_name=_("Portals"))
    open_in_new_tab = models.BooleanField(verbose_name=_('Open the link in a new tab'), default=True)
    attachments = GenericRelation(settings.PAPERCLIP_ATTACHMENT_MODEL)

    class Meta:
        verbose_name = _('Menu item')
        verbose_name_plural = _('Menu items')

    def __str__(self):
        return self.title
