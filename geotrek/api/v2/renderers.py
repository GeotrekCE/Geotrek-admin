import pygal
from django.conf import settings
from django.utils import translation
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from pygal.style import LightSolarizedStyle
from rest_framework.renderers import BaseRenderer


class SVGProfileRenderer(BaseRenderer):
    media_type = "image/svg+xml"
    format = "svg"

    def render(self, data, media_type=None, renderer_context=None):
        """
        Plot the altimetric graph in SVG using PyGal.
        Most of the job done here is dedicated to preparing
        nice labels scales.
        """
        ceil_elevation = data["limits"]["ceil"]
        floor_elevation = data["limits"]["floor"]
        profile = data["profile"]
        config = dict(
            show_legend=False,
            print_values=False,
            show_dots=False,
            zero=floor_elevation,
            value_formatter=lambda v: "%d" % v,
            margin=settings.ALTIMETRIC_PROFILE_FONTSIZE,
            width=settings.ALTIMETRIC_PROFILE_WIDTH,
            height=settings.ALTIMETRIC_PROFILE_HEIGHT,
            title_font_size=settings.ALTIMETRIC_PROFILE_FONTSIZE,
            label_font_size=0.8 * settings.ALTIMETRIC_PROFILE_FONTSIZE,
            major_label_font_size=settings.ALTIMETRIC_PROFILE_FONTSIZE,
            js=[],
        )

        style = LightSolarizedStyle
        style.background = settings.ALTIMETRIC_PROFILE_BACKGROUND
        style.colors = (settings.ALTIMETRIC_PROFILE_COLOR,)
        style.font_family = settings.ALTIMETRIC_PROFILE_FONT
        line_chart = pygal.XY(fill=True, style=style, **config)
        lang = renderer_context["request"].GET.get("language", get_language())
        with translation.override(lang):
            line_chart.x_title = _("Distance (m)")
            line_chart.y_title = _("Altitude (m)")
            line_chart.show_minor_x_labels = False
            line_chart.x_labels_major_count = 5
            line_chart.show_minor_y_labels = False
            line_chart.truncate_label = 50
            line_chart.range = [floor_elevation, ceil_elevation]
            line_chart.no_data_text = _("Altimetry data not available")
            line_chart.add("", [(int(v[0]), int(v[3])) for v in profile])
            return line_chart.render()
