from crispy_forms.layout import LayoutObject

from django.template import Template
from django.template.loader import render_to_string
from django.utils.safestring import SafeString


class Formset(LayoutObject):
    """
    Renders an entire formset, as though it were a Field.
    Accepts the name (as a string) of formset as defined in the context.

    Examples:
        Formset('contact_formset')
        Formset('contact_formset', legend=_('Contacts'))
    """

    template = "common/layout/formset.html"

    def __init__(self, formset_context_name, legend=None, template=None):

        self.formset_context_name = formset_context_name
        self.legend = legend
        if template:
            self.template = template

    def render(self, form, form_style, context, **kwargs):
        formset = context.get(self.formset_context_name)
        if self.legend:
            legend = Template(str(self.legend)).render(context)
        else:
            legend = SafeString("")

        context.update({'formset': formset, "legend": legend})
        return render_to_string(self.template, context.flatten())
