import os
import mimetypes

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import slugify

from caminae.common.models import FileType


class AttachmentManager(models.Manager):

    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id,
                           object_id=obj.id)


def attachment_upload(instance, filename):
    """Stores the attachment in a "per module/appname/primary key" folder"""
    name, ext = os.path.splitext(filename)
    renamed = slugify(instance.title or name) + ext
    return 'paperclip/%s/%s/%s' % (
        '%s_%s' % (instance.content_object._meta.app_label,
                   instance.content_object._meta.object_name.lower()),
                   instance.content_object.pk,
                   renamed)


class Attachment(models.Model):

    objects = AttachmentManager()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    attachment_file = models.FileField(_('Attachment'), upload_to=attachment_upload, max_length=512)
    filetype = models.ForeignKey(FileType, verbose_name=_('File type'))

    creator = models.ForeignKey(User, related_name="created_attachments", verbose_name=_('Creator'),
                                help_text=_("User that uploaded"))
    author = models.CharField(blank=True, default='', max_length=128, db_column='auteur', verbose_name=_('Author'),
                              help_text=_("Original creator"))
    title = models.CharField(blank=True, default='', max_length=128, db_column='titre', verbose_name=_(u"Title"),
                             help_text=_("Official title"))
    legend = models.CharField(blank=True, default='', max_length=128, db_column='legende', verbose_name=_(u"Legend"),
                              help_text=_("Details"))

    date_insert = models.DateTimeField(editable=False, auto_now_add=True, verbose_name=_(u"Insertion date"))
    date_update = models.DateTimeField(editable=False, auto_now=True, verbose_name=_(u"Update date"))

    class Meta:
        db_table = "fl_t_fichier"
        ordering = ['-date_insert']
        permissions = (
            ('delete_foreign_attachments', 'Can delete foreign attachments'),
        )

    def __unicode__(self):
        return '%s attached %s' % (self.creator.username, self.attachment_file.name)

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]

    @property
    def mimetype(self):
        mt = mimetypes.guess_type(self.attachment_file.name, strict=True)[0]
        if mt is None:
            return ('application', 'octet-stream')
        return mt.split('/')

    @property
    def is_image(self):
        return self.mimetype[0].startswith('image')
