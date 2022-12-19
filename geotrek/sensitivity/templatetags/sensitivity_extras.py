import logging
import calendar

from django import template
from urllib.parse import quote

logger = logging.getLogger(__name__)

register = template.Library()


@register.filter
def month_abbr(month_number: str) -> str:
    month_number = int(month_number)
    return calendar.month_abbr[month_number]


@register.simple_tag
def svg_thumbnail(
    filetype: str,
    width: int = 100,
    height: int = 100,
    fillcolor: str = '#dddddd',
    textcolor: str = '#333'
) -> str:
    svg = quote(f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
            <rect width="{width}" height="{height}" style="fill:{fillcolor};" />
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" style="fill:{textcolor};font-size:10px;font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';">
              {filetype}
            </text>
          </svg>
          """, safe='~()*!.\'')
    return f"data:image/svg+xml;charset=utf-8,{svg}"
