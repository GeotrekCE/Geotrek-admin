from django.contrib.contenttypes.admin import GenericTabularInline

from geotrek.common.models import Attachment


class AttachmentInline(GenericTabularInline):
    model = Attachment
    extra = 0
