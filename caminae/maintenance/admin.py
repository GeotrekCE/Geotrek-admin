# -*- coding: utf-8 -*-


from django.contrib import admin

from caminae.maintenance.models import (
        Contractor, InterventionStatus, InterventionTypology, InterventionDisorder
)


admin.site.register(Contractor)
admin.site.register(InterventionStatus)
admin.site.register(InterventionTypology)
admin.site.register(InterventionDisorder)

