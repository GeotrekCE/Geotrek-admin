# -*- encoding: utf-8 -*-

from geotrek.common.models import Theme
from geotrek.common.parsers import ExcelParser, AttachmentParserMixin, FatalImportError
from geotrek.tourism.models import InformationDesk, InformationDeskType
from geotrek.trekking.models import (Trek, Practice, Accessibility, TrekRelationship)
from geotrek.trekking.parsers import TrekParser
from geotrek.zoning.parsers import CityParser


class CG44ExcelTrekParser(AttachmentParserMixin, ExcelParser):
    model = Trek
    update_only = True
    warn_on_missing_fields = True
    eid = 'eid2'
    duplicate_eid_allowed = True
    information_desk_type_name = u"Office du tourisme"
    fields = {
        'eid2': 'Identifiant',
        'description_teaser': 'DescriptifCourt',
        'description': 'DescriptifLong',
    }
    m2m_fields = {
        'information_desks': ('Tel', 'Contact', 'Mail'),
    }
    non_fields = {
        'attachments': 'Photos',
    }

    def start(self):
        super(CG44ExcelTrekParser, self).start()
        try:
            self.information_desk_type = InformationDeskType.objects.get(label=self.information_desk_type_name)
        except InformationDeskType.DoesNotExist:
            raise FatalImportError(u"Information desk type '{name}' does not exists in Geotrek-Admin. Please add it.".format(name=self.information_desk_type_name))

    def filter_information_desks(self, src, val):
        tel, contact, mail = val
        if not contact:
            return []
        information_desk = self.obj.information_desks.first()
        if not information_desk:
            information_desk = InformationDesk(type=self.information_desk_type)
        information_desk.phone = tel
        information_desk.name = contact
        information_desk.email = mail
        information_desk.save()
        return [information_desk]


class CG44PedestreTrekParser(TrekParser):
    warn_on_missing_fields = True
    eid = 'eid'
    fields = {
        'eid': 'NUM_OBJ',
        'name': 'FIRST_ALIA',
        'duration': 'FIRST_PARC',
        'difficulty': 'FIRST_DIFF',
        'eid2': 'FIRST_GENC',
        'route': 'FIRST_CARA',
        'practice': 'FIRST_USAG',
        'geom': 'geom',
    }
    m2m_fields = {
        'accessibilities': 'FIRST_USAG',
        'themes': 'FIRST_AVIS',
    }
    non_fields = {
        'related_treks': 'FIRST_LIAI',
    }
    field_options = {
        'route': {'mapping': {u"Boucle": u"Boucle", u"Itinerance": u"Itinérance"}, 'partial': True},
        'themes': {'mapping': {u"VIGNOBLE": u"Vignoble", u"LITTORAL": u"Littoral", u"FLEUVE ET RIVIERE": u"Fleuve et rivière", u"CAMPAGNE": u"Campagne", u"MARAIS": u"Marais", u"PATRIMOINE": u"Patrimoine", u"INCONTOURNABLE": u"Incontournables"}},
    }
    FIRST_ALIA_to_pk = {}
    relationships = []

    def end(self):
        for pk_a, name_b in self.relationships:
            try:
                pk_b = self.FIRST_ALIA_to_pk[name_b]
            except KeyError:
                self.add_warning(u"Bad value '{name}' for field FIRST_LIAI (separated by {separator}). No trek with this name in data to import.".format(name=name_b, separator=self.separator))
                continue
            TrekRelationship.objects.get_or_create(
                trek_a=Trek.objects.get(pk=pk_a),
                trek_b=Trek.objects.get(pk=pk_b),
                is_circuit_step=True
            )
        super(CG44PedestreTrekParser, self).end()

    def parse_row(self, row):
        super(CG44PedestreTrekParser, self).parse_row(row)
        if self.obj:
            self.FIRST_ALIA_to_pk[row['FIRST_ALIA']] = self.obj.pk

    def filter_eid(self, src, val):
        return 'P' + str(val)

    def filter_name(self, src, val):
        return val.split(':', 1)[1].strip()

    def filter_practice(self, src, val):
        val = val.split(self.separator)[0]
        val = val.strip()
        if val != u"Pédestre":
            self.add_warning(u"Bad first value '{val}' for field {src} (separated by '{separator}'). Should be 'Pédestre'.".format(val=val, src=src, separator=self.separator))
            return None
        return self.filter_fk(src, val, Practice, 'name')

    def filter_accessibilities(self, src, val):
        if not val or self.separator not in val:
            return []
        val = val.split(self.separator, 1)[1]
        return self.filter_m2m(src, val, Accessibility, 'name')

    def save_related_treks(self, src, val):
        if not val:
            return
        val = val.split(self.separator)
        self.relationships += [(self.obj.pk, name.strip()) for name in val]


class CG44AVeloTrekParser(TrekParser):
    warn_on_missing_fields = True
    eid = 'eid'
    fields = {
        'eid': 'ID_LOCAL',
        'name': 'INTITULE',
        'practice': 'USAGE',
        'duration': 'DUREE',
        'difficulty': 'NIVEAU',
        'route': 'TYPE',
        'eid2': 'ID_LAD',
        'geom': 'geom',
    }
    m2m_fields = {
        'themes': ('THEME', 'PRIORITE'),
    }
    non_fields = {
        'related_treks': ('ID_ITI', 'ORDRE_ETAP'),
    }
    field_options = {
        'difficulty': {'mapping': {1: u"Facile", 2: u"Moyen", 3: u"Difficile"}},
        'route': {'mapping': {1: u"Boucle", 2: u"Itinérance"}},
    }
    relationships = {}

    def end(self):
        for treks in self.relationships.itervalues():
            for etap, trek_a in treks.items():
                trek_b = treks.get(etap + 1)
                if not trek_b:
                    continue
                TrekRelationship.objects.get_or_create(
                    trek_a=trek_a,
                    trek_b=trek_b,
                    is_circuit_step=True
                )
        super(CG44AVeloTrekParser, self).end()

    def filter_eid(self, src, val):
        return 'V' + str(val)

    def filter_themes(self, src, val):
        val_theme, val_priorite = val
        val_theme = str(val_theme)
        val_theme = self.filter_m2m(src, val_theme, Theme, 'label', {'1': u"Vignoble", '2': u"Littoral", '3': u"Fleuve et rivière", '4': u"Campagne", '5': u"Marais", '6': u"Patrimoine", '7': u"Incontournables"})
        if val_priorite == 1:
            try:
                val_priorite = [Theme.objects.get(label='Incontournables')]
            except Theme.DoesNotExist:
                self.add_warning(u"Theme 'Incontournables' does not exists in Geotrek-Admin. Please add it.")
                val_priorite = []
        else:
            val_priorite = []
        return val_theme + val_priorite

    def save_related_treks(self, src, val):
        iti, etap = val
        if not iti or etap == 0:
            return
        self.relationships.setdefault(iti, {})
        self.relationships[iti][int(etap)] = self.obj


class CG44CityParser(CityParser):
    warn_on_missing_fields = True
    fields = {
        'code': 'INSEE',
        'name': 'NOM',
        'geom': 'geom',
    }
