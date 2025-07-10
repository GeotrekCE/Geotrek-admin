from django.core.exceptions import ValidationError
from django.template import Context, Template
from django.utils.translation import gettext_lazy as _


def validate_html_template(template):
    context = Context({"object": {"eid": "123456789"}})
    try:
        compiled = Template(template)
        compiled.render(context)  # check Django templating
    except Exception as e:
        raise ValidationError(
            _("Incorrect syntax: %(error)s"),
            params={"error": str(e)},
        )
