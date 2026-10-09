def weekday_between(start_date, end_date):
    nb_days = (end_date - start_date).days + 1

    if nb_days >= 7:
        return list(range(0, 7))

    start_weekday = start_date.weekday()
    return [(start_weekday + i) % 7 for i in range(nb_days)]
