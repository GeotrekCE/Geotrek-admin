from datetime import date
from calendar import monthrange


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
    tpl = '"{m}": ["UTC(01/{str_month}->{str_lmonth}/{str_month})", "ANY(00:00->23:59)"]'
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
    return '{{{{{}}}}}'.format(','.join(aatimes_list))
