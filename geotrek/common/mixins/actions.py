from django.db import transaction
from django.db.models import ForeignKey, ManyToManyField
from django.utils.translation import gettext_lazy as _


@transaction.atomic
def apply_merge(modeladmin, request, queryset):
    main = queryset[0]
    tail = queryset[1:]
    if not tail:
        return
    name = " + ".join(queryset.values_list(modeladmin.merge_field, flat=True))
    fields = main._meta.get_fields()

    for field in fields:
        if field.remote_field:
            remote_field = field.remote_field.name
            if isinstance(field.remote_field, ForeignKey):
                field.remote_field.model.objects.filter(
                    **{f"{remote_field}__in": tail}
                ).update(**{remote_field: main})
            elif isinstance(field.remote_field, ManyToManyField):
                for element in field.remote_field.model.objects.filter(
                    **{f"{remote_field}__in": tail}
                ):
                    getattr(element, remote_field).add(main)
    max_length = main._meta.get_field(modeladmin.merge_field).max_length
    name = name if not len(name) > max_length - 4 else f"{name[: max_length - 4]} ..."
    setattr(main, modeladmin.merge_field, name)
    main.save()
    for element_to_delete in tail:
        element_to_delete.delete()


apply_merge.short_description = _("Merge")


class MergeActionMixin:
    actions = [apply_merge]
