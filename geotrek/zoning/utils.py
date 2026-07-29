def month_between(start_date, end_date):
    nb_month = (
        (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month) + 1
    )

    if nb_month >= 12:
        return list(range(1, 13))

    start_month = start_date.month
    return [(start_month - 1 + i) % 12 + 1 for i in range(nb_month)]


def weekday_between(start_date, end_date):
    nb_days = (end_date - start_date).days + 1

    if nb_days >= 7:
        return list(range(0, 7))

    start_weekday = start_date.weekday()
    return [(start_weekday + i) % 7 for i in range(nb_days)]
