from django.db.models import TextChoices
from django.utils.translation import gettext as _


class Practicability(TextChoices):
    PRACTICABLE = "practicable", _("Practicable")
    POSSIBLY_PRACTICABLE = "possibly_practicable", _("Possibly practicable")
    NOT_PRACTICABLE = "not_practicable", _("Not practicable")
