from django.db.models import IntegerChoices
from django.utils.dates import MONTHS, WEEKDAYS


class WeekdayChoices(IntegerChoices):
    MONDAY = 0, WEEKDAYS[0].title()
    TUESDAY = 1, WEEKDAYS[1].title()
    WEDNESDAY = 2, WEEKDAYS[2].title()
    THURSDAY = 3, WEEKDAYS[3].title()
    FRIDAY = 4, WEEKDAYS[4].title()
    SATURDAY = 5, WEEKDAYS[5].title()
    SUNDAY = 6, WEEKDAYS[6].title()
