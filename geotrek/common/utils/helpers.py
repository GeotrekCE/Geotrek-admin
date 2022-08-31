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


def clone_object(obj, attrs={}):

    # we start by building a "flat" clone
    clone = obj._meta.model.objects.get(pk=obj.pk)
    clone.pk = None
    clone.id = None
    clone.uuid = uuid.uuid4()
    if 'name' in [field.name for field in obj._meta.get_fields()]:
        clone.name = f'{obj.name} (copy)'
    # if caller specified some attributes to be overridden,
    # use them

    for key, value in attrs.items():
        setattr(clone, key, value)

    # save the partial clone to have a valid ID assigned
    clone.save()

    if issubclass(obj.__class__, Topology) and settings.TREKKING_TOPOLOGY_ENABLED:
        new_topology = Topology.objects.create()
        new_topology.mutate(obj.topo_object, delete=False)

    # Scan field to further investigate relations
    fields = clone._meta.get_fields()
    for field in fields:
        # Manage M2M fields by replicating all related records
        # found on parent "obj" into "clone"
        if not field.auto_created and field.many_to_many:
            for row in getattr(obj, field.name).all():
                getattr(clone, field.name).add(row)

        # Manage 1-N and 1-1 relations by cloning child objects
        if field.auto_created and field.is_relation:
            if field.many_to_many:
                # do nothing
                pass
            else:
                # provide "clone" object to replace "obj"
                # on remote field
                attrs = {
                    field.remote_field.name: clone
                }
                children = field.related_model.objects.filter(**{field.remote_field.name: obj})

                for child in children:
                    clone_object(child, attrs)
    for attachment in Attachment.objects.filter(object_id=obj.pk):
        clone_attachment(attachment, clone, 'attachment_file')
    for accessibility_attachment in AccessibilityAttachment.objects.filter(object_id=obj.pk):
        clone_attachment(accessibility_attachment, clone, 'attachment_accessibility_file')
    return clone
