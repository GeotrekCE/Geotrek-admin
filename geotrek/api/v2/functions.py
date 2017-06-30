from django.db.models import Func, F


def Transform(field_name, srid):
    """
    ST_TRANSFORM postgis function
    """
    return Func(F(field_name), srid, function='ST_TRANSFORM')
