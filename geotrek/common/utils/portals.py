from django.template.exceptions import TemplateDoesNotExist
from django.template.loader import get_template


def smart_get_template_by_portal(model, portal_id, suffix):
    for appname, modelname in [
        (model._meta.app_label, model._meta.object_name.lower()),
        ("mapentity", "override"),
        ("mapentity", "mapentity"),
    ]:
        try:
            template_name = "%s/portal_%s/%s%s" % (
                appname,
                portal_id,
                modelname,
                suffix,
            )
            get_template(template_name)  # Will raise if not exist
            return template_name
        except TemplateDoesNotExist:
            pass
    return None
