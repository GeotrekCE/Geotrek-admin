import factory

from django.contrib.contenttypes.models import ContentType

from geotrek.authent.factories import UserFactory
from geotrek.common.factories import FileTypeFactory
from geotrek.common.utils.testdata import get_dummy_uploaded_file
from . import models


class AttachmentFactory(factory.Factory):
    """
    Create an attachment. You must provide an 'obj' keywords,
    the object (saved in db) to which the attachment will be bound.
    """

    FACTORY_FOR = models.Attachment

    attachment_file = get_dummy_uploaded_file()
    filetype = factory.SubFactory(FileTypeFactory)

    creator = factory.SubFactory(UserFactory)
    title = factory.Sequence(u"Title {0}".format)
    legend = factory.Sequence(u"Legend {0}".format)

    # date_insert, date_update

    @classmethod
    def _prepare(cls, create, obj=None, **kwargs):
        kwargs['content_type'] = ContentType.objects.get_for_model(obj)
        kwargs['object_id'] = obj.pk
        return super(AttachmentFactory, cls)._prepare(create, **kwargs)

