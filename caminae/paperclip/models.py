import os
import mimetypes

from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.utils.translation import ugettext_lazy as _

from caminae.common.models import FileType


class AttachmentManager(models.Manager):
    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id,
                           object_id=obj.id)

class Attachment(models.Model):
    def attachment_upload(instance, filename):
        """Stores the attachment in a "per module/appname/primary key" folder"""
        return 'paperclip/%s/%s/%s' % (
            '%s_%s' % (instance.content_object._meta.app_label,
                       instance.content_object._meta.object_name.lower()),
                       instance.content_object.pk,
                       filename)

    objects = AttachmentManager()

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    attachment_file = models.FileField(_('Attachment'), upload_to=attachment_upload)
    filetype = models.ForeignKey(FileType)

    creator = models.ForeignKey(User, related_name="created_attachments", verbose_name=_('Creator'))
    title = models.CharField(blank=True, default='', max_length=128, db_column='titre', verbose_name=_(u"Title"))
    legend = models.CharField(blank=True, default='', max_length=128, db_column='legende', verbose_name=_(u"Legend"))

    date_insert = models.DateTimeField(editable=False, auto_now_add=True, verbose_name=_(u"Insertion date"))
    date_update = models.DateTimeField(editable=False, auto_now=True, verbose_name=_(u"Update date"))

    class Meta:
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
        return mimetypes.guess_type(self.attachment_file.name, strict=True)[0].split('/')

    @property
    def is_image(self):
        return self.mimetype[0].startswith('image')
