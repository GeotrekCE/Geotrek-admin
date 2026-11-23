from calendar import monthrange
from datetime import date

from django.conf import settings
from django.contrib.gis.db import models
from django.contrib.gis.db.models.functions import Transform
from django.db.models import Case, F, Value, When
from django.db.models.functions import Coalesce

from geotrek.common.functions import Buffer, GeometryType


def annotate_display_geom(qs, field_name="geom_display", srid=None):
    """Annotate queryset so Point geometries become circle polygons of their species radius."""
    effective_radius = Coalesce(
        F("species__radius"), Value(settings.SENSITIVITY_DEFAULT_RADIUS)
    )
    point_geom = F("geom")
    circle_geom = Buffer(F("geom"), effective_radius, 16)
    default_geom = F("geom")
    if srid is not None:
        point_geom = Transform(point_geom, srid)
        circle_geom = Transform(circle_geom, srid)
        default_geom = Transform(default_geom, srid)
    output_srid = srid if srid is not None else settings.SRID
    return qs.alias(geom_type=GeometryType(F("geom"))).annotate(
        **{
            field_name: Case(
                When(
                    geom_type="POINT",
                    then=Case(
                        When(species__radius__lte=0, then=point_geom),
                        default=circle_geom,
                        output_field=models.GeometryField(srid=output_srid),
                    ),
                ),
                default=default_geom,
                output_field=models.GeometryField(srid=output_srid),
            )
        }
    )


def openair_atimes(month: int) -> str:
    """Format month number to OpenAir ATime item

    :param month: Months (1-12)
    :type month: int
    :return: ATimes item
    :rtype: str
    """
    year = date.today().year
    str_lmonth = str(monthrange(year, month)[1]).zfill(2)
    str_month = str(month).zfill(2)
    tpl = (
        '"{m}": ["UTC(01/{str_month}->{str_lmonth}/{str_month})", "ANY(00:00->23:59)"]'
    )
    return tpl.format(m=str(month), str_month=str_month, str_lmonth=str_lmonth)


def openair_atimes_concat(row) -> str:
    months_fields = [
        row.species.period01,
        row.species.period02,
        row.species.period03,
        row.species.period04,
        row.species.period05,
        row.species.period06,
        row.species.period07,
        row.species.period08,
        row.species.period09,
        row.species.period10,
        row.species.period11,
        row.species.period12,
    ]
    aatimes_list = []
    for i in range(12):
        if months_fields[i]:
            aatimes_list.append(openair_atimes(i + 1))
    return "{{{{{}}}}}".format(",".join(aatimes_list))
