from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.timezone import now

from geotrek.common.models import Attachment, AccessibilityAttachment


@receiver(post_save, sender=Attachment)
@receiver(post_save, sender=AccessibilityAttachment)
@receiver(post_delete, sender=Attachment)
@receiver(post_delete, sender=AccessibilityAttachment)
def update_content_object_date_update(sender, instance, *args, **kwargs):
    """ after each creation / edition / deletion, increment date_updated to avoid object cache """
    content_object = instance.content_object
    if content_object and hasattr(content_object, 'date_update'):
        content_object.date_update = now()
        content_object.save(update_fields=['date_update'])
