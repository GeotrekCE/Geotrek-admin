import re
import uuid

import pygal
from django.conf import settings
from django.utils import translation
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from pygal.style import LightSolarizedStyle
from rest_framework import renderers
from rest_framework.compat import INDENT_SEPARATORS, LONG_SEPARATORS, SHORT_SEPARATORS
from rest_framework.renderers import BaseRenderer
from rest_framework.utils import json


class RawJSON:
    """Wrapper for pre-serialized JSON strings (e.g. from PostGIS ST_AsGeoJSON)."""

    __slots__ = ("value",)

    def __init__(self, value: str):
        self.value = value

    def _parsed(self):
        return json.loads(self.value)

    def get(self, key, default=None):
        return self._parsed().get(key, default)

    def __getitem__(self, key):
        return self._parsed()[key]


class RawJSONRenderer(renderers.JSONRenderer):
    """
    JSONRenderer that embeds RawJSON instances verbatim into the output
    without parsing them into Python objects and re-serializing them.
    """

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if data is None:
            return b""

        renderer_context = renderer_context or {}
        indent = self.get_indent(accepted_media_type, renderer_context)

        if indent is None:
            separators = SHORT_SEPARATORS if self.compact else LONG_SEPARATORS
        else:
            separators = INDENT_SEPARATORS

        raw_values = []
        sentinel = f"__RAWJSON_{uuid.uuid4().hex}_"
        base_encoder = self.encoder_class

        class _RawJSONEncoder(base_encoder):
            def default(self, obj):
                if isinstance(obj, RawJSON):
                    idx = len(raw_values)
                    raw_values.append(obj.value)
                    return f"{sentinel}{idx}__"
                return super().default(obj)

        ret = json.dumps(
            data,
            cls=_RawJSONEncoder,
            indent=indent,
            ensure_ascii=self.ensure_ascii,
            allow_nan=not self.strict,
            separators=separators,
        )

        if raw_values:
            ret = re.sub(
                rf'"{sentinel}(\d+)__"',
                lambda m: raw_values[int(m.group(1))],
                ret,
            )

        # Preserve DRF JSONRenderer escaping for JS-safe line terminators
        ret = ret.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
        return ret.encode()


class RawGeoJSONRenderer(RawJSONRenderer):
    format = "geojson"
    media_type = "application/geo+json"


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
            value_formatter=lambda v: f"{v}",
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
