from django.core.exceptions import ValidationError
from django.test import TestCase

from geotrek.common.validators import validate_html_template


class TemplateHTMLValidatorTEstCase(TestCase):
    def test_template_is_valid(self):
        value = (
            "<a href='http://test/object/{{object.eid|safe}}'>{{object.eid|safe}}</a>"
        )
        validate_html_template(value)

    def test_template_is_invalid(self):
        value = (
            "<a href='http://test/object/{% object.eid|safe %}'>{{object.eid|safe}}</a>"
        )

        with self.assertRaises(ValidationError):
            validate_html_template(value)
