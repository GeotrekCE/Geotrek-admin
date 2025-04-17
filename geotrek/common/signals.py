from django.contrib.admin.models import DELETION, LogEntry
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.timezone import now
from mapentity.middleware import get_internal_user

from geotrek.common.models import AccessibilityAttachment, Attachment, HDViewPoint


def log_cascade_deletion(sender, instance, related_model, cascading_field):
    related_objects = related_model.objects.filter(
        **{f"{cascading_field}": instance}
    ).all()
    if related_objects:
        user = get_internal_user()
        model_number = ContentType.objects.get_for_model(related_model)
        for related_object in related_objects:
            LogEntry.objects.create(
                user=user,
                content_type=model_number,
                object_id=related_object.pk,
                object_repr=str(related_object),
                action_flag=DELETION,
                change_message=f"Deleted by cascade from {sender.__name__} {instance.pk} - {instance}",
            )


@receiver(post_save, sender=Attachment)
@receiver(post_save, sender=AccessibilityAttachment)
@receiver(post_save, sender=HDViewPoint)
@receiver(post_delete, sender=Attachment)
@receiver(post_delete, sender=AccessibilityAttachment)
@receiver(post_delete, sender=HDViewPoint)
def update_content_object_date_update(sender, instance, *args, **kwargs):
    """after each creation / edition / deletion, increment date_updated to avoid object cache"""
    content_object = instance.content_object
    if content_object and hasattr(content_object, "date_update"):
        content_object.date_update = now()
        content_object.save(update_fields=["date_update"])
