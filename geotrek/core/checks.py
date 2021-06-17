from geotrek.core.forms import PathForm
from django.conf import settings
from django.core import checks

MAP_SETTINGS_KEYS = {
    PathForm: 'path'
}


def check_fields_to_hide_on_form(errors, form_class):
    form_fields = form_class(hide_fields=False)._meta.fields
    form_key = MAP_SETTINGS_KEYS[form_class]
    for field_to_hide in settings.HIDDEN_FORM_FIELDS.get(form_key, []):
        if field_to_hide not in form_fields:
            errors.append(
                checks.Error(
                    f"Cannot hide field '{field_to_hide}'",
                    hint="Field not included in form",
                    # Diplay dotted path only
                    obj=str(form_class).split(" ")[1].strip(">").strip("'")
                )
            )


def check_fields_to_hide(app_configs, **kwargs):
    errors = []
    check_fields_to_hide_on_form(errors, PathForm)
    # errors = check_fields_to_hide_on_form(errors, TrailForm)
    # errors = check_fields_to_hide_on_form(errors, TrekForm)
    # ...
    return errors
