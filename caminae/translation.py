from modeltranslation.translator import translator, TranslationOptions

from caminae.maintenance import models as maintenance_models


## Maintenance app ##

class InterventionStatusTO(TranslationOptions):
    fields = ('status',)


class InterventionTypologyTO(TranslationOptions):
    fields = ('typology', )


class InterventionDisorderTO(TranslationOptions):
    fields = ('disorder', )


translator.register(maintenance_models.InterventionStatus, InterventionStatusTO)
translator.register(maintenance_models.InterventionTypology, InterventionTypologyTO)
translator.register(maintenance_models.InterventionDisorder, InterventionDisorderTO)



