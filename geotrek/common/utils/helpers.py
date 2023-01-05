import uuid

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

from geotrek.core.models import Topology
from geotrek.common.models import Attachment
from geotrek.common.models import AccessibilityAttachment


def clone_attachment(attachment, clone, field_file):
    fields = attachment._meta.get_fields()
    clone_values = {}
    for field in fields:
        if not field.auto_created:
            if field.name == "pk":
                continue
            elif field.name == "uuid":
                clone_values['uuid'] = uuid.uuid4()
            elif field.name == "content_object":
                clone_values['content_object'] = clone
            elif field.name == field_file:
                attachment_content = getattr(attachment, field_file).read()
                attachment_name = getattr(attachment, field_file).name.split("/")[-1]
                clone_values[field_file] = SimpleUploadedFile(attachment_name, attachment_content)
            else:
                clone_values[field.name] = getattr(attachment, field.name, None)
    attachment._meta.model.objects.create(**clone_values)
