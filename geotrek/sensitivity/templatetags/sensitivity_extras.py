from django import template
import calendar
from urllib.parse import quote

register = template.Library()


@register.filter
def month_abbr(month_number):
    month_number = int(month_number)
    return calendar.month_abbr[month_number]


@register.filter
def svg_thumbnail(filetype):
    svg = quote(f"""<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">
            <rect width="100" height="100" style="fill:#dddddd;" />
            <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" style="fill:#333;font-size:10px;font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', 'Liberation Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji';">
              {filetype}
            </text>
          </svg>
          """, safe='~()*!.\'')
    return f"data:image/svg+xml;charset=utf-8,{svg}"
