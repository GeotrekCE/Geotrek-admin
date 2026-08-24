from django.db.models import IntegerChoices, TextChoices
from django.utils.dates import MONTHS, WEEKDAYS
from django.utils.translation import gettext_lazy as _


class Practicability(TextChoices):
    PRACTICABLE = "practicable", _("Practicable")
    UNDER_CONDITION_PRACTICABLE = (
        "under_condition_practicable",
        _("Under condition practicable"),
    )
    NOT_PRACTICABLE = "not_practicable", _("Not practicable")


class VigilanceLevel(TextChoices):
    INFORMATION = "information", _("Information")
    VIGILANCE = (
        "vigilance",
        _("Vigilance"),
    )
    ALERT = "alert", _("Alert")


class WeekdayChoices(IntegerChoices):
    MONDAY = 0, WEEKDAYS[0].title()
    TUESDAY = 1, WEEKDAYS[1].title()
    WEDNESDAY = 2, WEEKDAYS[2].title()
    THURSDAY = 3, WEEKDAYS[3].title()
    FRIDAY = 4, WEEKDAYS[4].title()
    SATURDAY = 5, WEEKDAYS[5].title()
    SUNDAY = 6, WEEKDAYS[6].title()


class MonthChoices(IntegerChoices):
    JANUARY = 1, MONTHS[1].title()
    FEBRUARY = 2, MONTHS[2].title()
    MARCH = 3, MONTHS[3].title()
    APRIL = 4, MONTHS[4].title()
    MAY = 5, MONTHS[5].title()
    JUNE = 6, MONTHS[6].title()
    JULY = 7, MONTHS[7].title()
    AUGUST = 8, MONTHS[8].title()
    SEPTEMBER = 9, MONTHS[9].title()
    OCTOBER = 10, MONTHS[10].title()
    NOVEMBER = 11, MONTHS[11].title()
    DECEMBER = 12, MONTHS[12].title()
