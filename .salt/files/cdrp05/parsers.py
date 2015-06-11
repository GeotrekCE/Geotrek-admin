# -*- encoding: utf-8 -*-

from django.conf import settings
from django.contrib.gis.geos import Point

from geotrek.common.parsers import SitraParser, OpenSystemParser
from geotrek.tourism.models import TouristicContent


class CDRP05Parser(SitraParser):
    api_key = 'v4Hwz5Fo'
    project_id = 1319
    model = TouristicContent
    eid = 'eid'
    fields = {
        'eid': 'id',
        'name': 'nom.libelleFr',
        'description': 'presentation.descriptifCourt.libelleFr',
        'contact': (
            'localisation.adresse.adresse1',
            'localisation.adresse.adresse2',
            'localisation.adresse.codePostal',
            'localisation.adresse.commune.nom',
            'informations.moyensCommunication',
        ),
        'email': 'informations.moyensCommunication',
        'website': 'informations.moyensCommunication',
        'geom': 'localisation.geolocalisation.geoJson.coordinates',
    }
    non_fields = {
        'attachments': 'illustrations',
    }
    natural_keys = {
        'category': 'label',
    }

    def filter_comm(self, val, code):
        if not val:
            return None
        for subval in val:
            if subval['type']['id'] == code:
                return subval['coordonnees']['fr']

    def filter_email(self, src, val):
        return self.filter_comm(val, 204)

    def filter_website(self, src, val):
        return self.filter_comm(val, 205)

    def filter_contact(self, src, val):
        (address1, address2, zipCode, commune, comm) = val
        tel = self.filter_comm(comm, 201)
        if tel:
            tel = u"Tél. " + tel
        lines = [line for line in [
            address1,
            address2,
            ' '.join([part for part in [zipCode, commune] if part]),
            tel,
        ] if line]
        return '<br>'.join(lines)

    def filter_geom(self, src, val):
        lng, lat = val
        geom = Point(float(lng), float(lat), srid=4326)  # WGS84
        geom.transform(settings.SRID)
        return geom


class CampingsParser(CDRP05Parser):
    selection_id = 33075
    constant_fields = {
        'category': u"Campings",
        'published': True,
    }


class ChambresDHotesParser(CDRP05Parser):
    selection_id = 33076
    constant_fields = {
        'category': u"Chambres d'hôtes",
        'published': True,
    }


class HotelsParser(CDRP05Parser):
    selection_id = 33077
    constant_fields = {
        'category': u"Hôtels",
        'published': True,
    }


class GitesDEtapeParser(CDRP05Parser):
    selection_id = 33079
    constant_fields = {
        'category': u"Gîtes d'étape",
        'published': True,
    }


class HebergementsInsolitesParser(CDRP05Parser):
    selection_id = 33080
    constant_fields = {
        'category': u"Hébergements insolites",
        'published': True,
    }


class AlimentationParser(CDRP05Parser):
    selection_id = 33081
    constant_fields = {
        'category': u"Alimentation",
        'published': True,
    }


class ResaParser(OpenSystemParser):
    login = 'concentrateurhautesalpes'
    password = 'bz7895nkex'
    model = TouristicContent
    eid = 'eid'
    update_only = True
    fields = {
        'eid': 'id_sitra',
        'reservation_id': 'id_opensystem',
    }
