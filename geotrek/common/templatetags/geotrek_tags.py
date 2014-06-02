from django import template


register = template.Library()


@register.assignment_tag
def is_topology_model(model):
    return hasattr(model, 'kind') and hasattr(model, 'offset')
