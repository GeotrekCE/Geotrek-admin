# -*- coding: utf-8 -*-

import json

import datetime
import requests
from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext as _

from geotrek.common.parsers import (AttachmentParserMixin, Parser,
                                    GlobalImportError)
from geotrek.tourism.models import TouristicContent, TouristicContentType1, TouristicContentType2


class TouristicContentSitraParser(AttachmentParserMixin, Parser):
    """Parser to import touristic contents from SITRA"""
    separator = None
    api_key = None
    project_id = None
    selection_id = None
    category = None
    type1 = None
    type2 = None
    source = None
    portal = None
    url = 'http://api.sitra-tourisme.com/api/v002/recherche/list-objets-touristiques/'
    model = TouristicContent
    eid = 'eid'
    fields = {
        'eid': 'id',
        'name': 'nom.libelleFr',
        'description': 'presentation.descriptifDetaille.libelleFr',
        'description_teaser': 'presentation.descriptifCourt.libelleFr',
        'contact': (
            'localisation.adresse.adresse1',
            'localisation.adresse.adresse2',
            'localisation.adresse.adresse3',
            'localisation.adresse.codePostal',
            'localisation.adresse.commune.nom',
            'informations.moyensCommunication',
        ),
        'email': 'informations.moyensCommunication',
        'website': 'informations.moyensCommunication',
        'geom': 'localisation.geolocalisation.geoJson.coordinates',
        'practical_info': (
            'ouverture.periodeEnClair.libelleFr',
            'informationsHebergementCollectif.capacite.capaciteTotale',
            'descriptionTarif.tarifsEnClair.libelleFr',
            'descriptionTarif.modesPaiement',
            'prestations.services',
            'localisation.geolocalisation.complement.libelleFr',
            'gestion.dateModification',
            'gestion.membreProprietaire.nom',
        ),
    }
    constant_fields = {
        'published': True,
    }
    m2m_constant_fields = {
    }
    non_fields = {
        'attachments': 'illustrations',
    }
    natural_keys = {
        'category': 'label',
        'type1': 'label',
        'type2': 'label',
        'source': 'name',
        'portal': 'name',
    }
    field_options = {
        'name': {'required': True},
        'geom': {'required': True},
    }

    def __init__(self, *args, **kwargs):
        super(TouristicContentSitraParser, self).__init__(*args, **kwargs)
        if self.category:
            self.constant_fields['category'] = self.category
        if self.type1:
            self.m2m_constant_fields['type1'] = self.type1
        if self.type2:
            self.m2m_constant_fields['type2'] = self.type2
        if self.source:
            self.m2m_constant_fields['source'] = self.source
        if self.portal:
            self.m2m_constant_fields['portal'] = self.portal

    @property
    def items(self):
        return self.root['objetsTouristiques']

    def next_row(self):
        size = 100
        skip = 0
        while True:
            params = {
                'apiKey': self.api_key,
                'projetId': self.project_id,
                'selectionIds': [self.selection_id],
                'count': size,
                'first': skip,
                'responseFields': [
                    'id',
                    'nom',
                    'presentation.descriptifCourt',
                    'presentation.descriptifDetaille',
                    'localisation.adresse',
                    'localisation.geolocalisation.geoJson.coordinates',
                    'localisation.geolocalisation.complement.libelleFr',
                    'informations.moyensCommunication',
                    'ouverture.periodeEnClair',
                    'informationsHebergementCollectif.capacite.capaciteTotale',
                    'informationsHebergementCollectif.hebergementCollectifType.libelleFr',
                    'descriptionTarif.tarifsEnClair',
                    'descriptionTarif.modesPaiement',
                    'prestations.services',
                    'gestion.dateModification',
                    'gestion.membreProprietaire.nom',
                ],
            }
            response = requests.get(self.url, params={'query': json.dumps(params)})
            if response.status_code != 200:
                msg = _(u"Failed to download {url}. HTTP status code {status_code}")
                raise GlobalImportError(msg.format(url=response.url, status_code=response.status_code))
            self.root = response.json()
            self.nb = int(self.root['numFound'])
            for row in self.items:
                yield row
            skip += size
            if skip >= self.nb:
                return

    def filter_attachments(self, src, val):
        result = []
        for subval in val or []:
            if 'nom' in subval:
                name = subval['nom'].get('libelleFr')
            else:
                name = None
            result.append((subval['traductionFichiers'][0]['url'], name, None))
        return result

    def normalize_field_name(self, name):
        return name

    def filter_eid(self, src, val):
        return unicode(val)

    def filter_comm(self, val, code, multiple=True):
        if not val:
            return None
        vals = [subval['coordonnees']['fr'] for subval in val if subval['type']['id'] == code]
        if multiple:
            return ' / '.join(vals)
        if vals:
            return vals[0]
        return None

    def filter_email(self, src, val):
        return self.filter_comm(val, 204, multiple=False)

    def filter_website(self, src, val):
        return self.filter_comm(val, 205, multiple=False)

    def filter_contact(self, src, val):
        (address1, address2, address3, zipCode, commune, comm) = val
        tel = self.filter_comm(comm, 201, multiple=True)
        if tel:
            tel = u"Tél. " + tel
        lines = [line for line in [
            address1,
            address2,
            address3,
            ' '.join([part for part in [zipCode, commune] if part]),
            tel,
        ] if line]
        return '<br>'.join(lines)

    def filter_practical_info(self, src, val):
        (ouverture, capacite, tarifs, paiement, services, localisation, datemodif, proprio) = val
        if ouverture:
            ouverture = u"<b>Ouverture:</b><br>" + u"<br>".join(ouverture.splitlines()) + u"<br>"
        if capacite:
            capacite = u"<b>Capacité totale:</b><br>" + str(capacite) + u"<br>"
        if tarifs:
            tarifs = u"<b>Tarifs:</b><br>" + u"<br>".join(tarifs.splitlines()) + u"<br>"
        if paiement:
            paiement = u"<b>Modes de paiement:</b><br>" + ", ".join([i['libelleFr'] for i in paiement]) + u"<br>"
        if services:
            services = u"<b>Services:</b><br>" + ", ".join([i['libelleFr'] for i in services]) + u"<br>"
        if localisation:
            localisation = u"<b>Accès:</b><br>" + u"<br>".join(localisation.splitlines()) + u"<br>"
        datemodif = datetime.datetime.strptime(datemodif[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        modif = u"<i>Fiche mise à jour par " + proprio + u" le " + datemodif + u"</i>"
        lines = [line for line in [
            ouverture,
            capacite,
            tarifs,
            paiement,
            services,
            localisation,
            modif,
        ] if line]
        return '<br>'.join(lines)

    def filter_description(self, src, val):
        return '<br>'.join(val.splitlines())

    def filter_description_teaser(self, src, val):
        return '<br>'.join(val.splitlines())

    def filter_geom(self, src, val):
        lng, lat = val
        geom = Point(float(lng), float(lat), srid=4326)  # WGS84
        geom.transform(settings.SRID)
        return geom


class HebergementsSitraParser(TouristicContentSitraParser):
    category = u"Hébergements"
    m2m_fields = {
        'type1': 'informationsHebergementCollectif.hebergementCollectifType.libelleFr',
    }

    def filter_type1(self, src, val):
        return self.apply_filter('type1', src, [val])


class EspritParcParser(AttachmentParserMixin, Parser):
    model = TouristicContent
    eid = 'eid'
    separator = None
    delete = True
    fields = {
        'eid': 'eid',
        'name': 'nomCommercial',
        'description': 'descriptionDetaillee',
        'practical_info': 'informationsPratiques',
        'category': 'type.0.label',
        'contact': (
            'contact.adresse',
            'contact.codePostal',
            'contact.commune',
            'contact.telephone',
            'contact.gsm',
            'contact.fax',
            'contact.facebook',
            'contact.twitter'
        ),
        'email': 'contact.courriel',
        'website': 'contact.siteWeb',
        'geom': 'geo',
    }

    constant_fields = {
        'published': True,
        'approved': True,
        'deleted': False,
    }

    field_options = {
        'name': {'required': True, },
        'geom': {'required': True, },
        'category': {'create': True},
    }

    natural_keys = {
        'category': 'label',
        'type1': 'label',
        'type2': 'label'
    }

    m2m_fields = {
        'type1': 'sousType.*.label',
        'type2': 'classement.*.labelType',
    }

    non_fields = {
        'attachments': 'photo',
    }

    def filter_attachments(self, src, val):
        result = []
        for subval in val or []:
            if 'url' in subval:
                result.append((subval['url'],
                               subval.get('legend', None),
                               subval.get('credits', None)))
        return result

    @property
    def items(self):
        return self.root['responseData']

    def next_row(self):
        response = requests.get(self.url)
        if response.status_code != 200:
            msg = _(u"Failed to download {url}. HTTP status code {status_code}")
            raise GlobalImportError(msg.format(url=response.url,
                                               status_code=response.status_code))

        self.root = response.json()
        self.nb = int(self.root['numFound'])

        for row in self.items:
            yield row

    def normalize_field_name(self, name):
        return name

    def filter_eid(self, src, val):
        return u"{}".format(val)

    def filter_contact(self, src, val):
        (address, zipCode, commune, telephone, gsm, fax, facebook, twitter) = val
        cp_com = u' '.join([part for part in (zipCode, commune) if part])
        return u'<br>'.join([part for part in (address, cp_com, telephone, gsm, fax, facebook, twitter) if part])

    def filter_geom(self, src, val):
        lng = val['lon']
        lat = val['lat']
        geom = Point(float(lng), float(lat), srid=4326)  # WGS84
        geom.transform(settings.SRID)
        return geom

    def filter_name(self, src, val):
        return val[:128]

    def filter_category(self, src, val):
        if not val:
            return None

        return self.apply_filter('category', src, val)

    def filter_type1(self, src, val):
        dst = []
        for subval in val or []:
            try:
                dst.append(TouristicContentType1.objects.get(category=self.obj.category, label=subval))
            except TouristicContentType1.DoesNotExist:
                self.add_warning(
                    _(u"Type 1 '{subval}' does not exist for category '{cat}'. Please add it").format(
                        subval=subval, cat=self.obj.category.label))
        return dst

    def filter_type2(self, src, val):
        dst = []
        for subval in val or []:
            try:
                dst.append(TouristicContentType2.objects.get(category=self.obj.category, label=subval))
            except TouristicContentType2.DoesNotExist:
                self.add_warning(_(u"Type 2 '{subval}' does not exist for category '{cat}'. Please add it").format(
                    subval=subval, cat=self.obj.category.label))
        return dst
