import os

import datetime

from mimetypes import guess_type
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext as _
from django.core.files.uploadedfile import UploadedFile

from geotrek.common.parsers import (AttachmentParserMixin, Parser,
                                    TourInSoftParser, GeotrekParser, ApidaeBaseParser, LEIParser, OpenStreetMapParser)
from geotrek.tourism.models import (InformationDesk, TouristicContent, TouristicEvent,
                                    TouristicContentType1, TouristicContentType2)
from geotrek.trekking.parsers import GeotrekTrekParser
from geotrek.trekking.models import Trek


class TouristicContentMixin:
    # Mixin which handle multiple type1/2 with the same name in different categories
    def get_to_delete_kwargs(self):
        # FIXME: use mapping if it exists
        kwargs = {}
        for dst, val in self.constant_fields.items():
            field = self.model._meta.get_field(dst)
            if isinstance(field, models.ForeignKey):
                natural_key = self.natural_keys[dst]
                try:
                    kwargs[dst] = field.remote_field.model.objects.get(**{natural_key: val})
                except field.remote_field.model.DoesNotExist:
                    return None
            else:
                kwargs[dst] = val
        for dst, val in self.m2m_constant_fields.items():
            assert not self.separator or self.separator not in val
            field = self.model._meta.get_field(dst)
            natural_key = self.natural_keys[dst]
            filters = {natural_key: subval for subval in val}
            if not filters:
                continue
            if dst in ('type1', 'type2'):
                filters['category'] = kwargs['category'].pk
            try:
                kwargs[dst] = field.remote_field.model.objects.get(**filters)
            except field.remote_field.model.DoesNotExist:
                return None
        if hasattr(self.model, 'provider') and self.provider is not None:
            kwargs['provider__exact'] = self.provider
        return kwargs


class ApidaeParser(AttachmentParserMixin, ApidaeBaseParser):
    """Parser to import "anything" from APIDAE"""
    eid = 'eid'
    fields = {
        'name': 'nom.libelleFr',
    }
    constant_fields = {
        'published': True,
    }
    non_fields = {
        'attachments': 'illustrations',
    }
    # Use for foreign keys. When the key is a foreign key, it will try to get the key's value.
    # In django : 'category' : 'label' -> category.label
    field_options = {
        'name': {'required': True},
        'geom': {'required': True},
    }
    responseFields = [
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
        'illustrations'
    ]

    def filter_eid(self, src, val):
        return str(val)

    def filter_geom(self, src, val):
        lng, lat = val
        geom = Point(float(lng), float(lat), srid=4326)  # WGS84
        geom.transform(settings.SRID)
        return geom

    def _filter_comm(self, val, code, multiple=True):
        """
        With the code of the section (mail, phone etc...), allow to get the right information from 'informations.moyensCommunication'
        When the information is multiple (val is a list), you can either get the first element (multiple=False),
        or get all elements separated by a / (multiple=True)
        """
        if not val:
            return None
        vals = [subval['coordonnees']['fr'] for subval in val if subval.get('type', {}).get('id') == code]
        if multiple:
            return ' / '.join(vals)
        if vals:
            return vals[0]
        return None


class AttachmentApidaeParserMixin(object):
    def filter_attachments(self, src, val):
        result = []
        for subval in val or []:
            copyright_attachment = subval.get('copyright', {}).get('libelleFr')
            legend_attachment = subval.get('legende', {}).get('libelleFr')
            name_attachment = subval.get('nom', {}).get('libelleFr')
            if legend_attachment:
                legend = legend_attachment
                if guess_type(legend)[0] in ['image/jpeg', 'image/png', 'image/x-ms-bmp']:
                    legend = name_attachment
            else:
                legend = name_attachment
            result.append((subval['traductionFichiers'][0]['url'], legend, copyright_attachment))
        return result


class InformationDeskApidaeParser(ApidaeParser):
    """Parser to import information desks from APIDAE"""
    type = None
    model = InformationDesk
    fields = {
        'eid': 'id',
        'description': 'presentation.descriptifDetaille.libelleFr',
        'geom': 'localisation.geolocalisation.geoJson.coordinates',
        'phone': 'informations.moyensCommunication',
        'email': 'informations.moyensCommunication',
        'website': 'informations.moyensCommunication',
        'photo': 'illustrations',
        'street': ('localisation.adresse.adresse1',
                   'localisation.adresse.adresse2',
                   'localisation.adresse.adresse3',),
        'postal_code': 'localisation.adresse.codePostal',
        'municipality': 'localisation.adresse.commune.nom',
        'name': 'nom.libelleFr',
    }
    constant_fields = {}
    natural_keys = {
        'type': 'label',
    }
    non_fields = {}
    responseFields = [
        'id',
        'nom',
        'presentation.descriptifDetaille',
        'localisation.adresse',
        'localisation.geolocalisation.geoJson.coordinates',
        'informations.moyensCommunication',
        'illustrations'
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constant_fields = self.constant_fields.copy()
        self.m2m_constant_fields = self.m2m_constant_fields.copy()
        self.field_options = self.field_options.copy()
        self.field_options['type'] = {'create': True}
        if self.type is not None:
            self.constant_fields['type'] = self.type

    def start(self):
        Parser.start(self)

    def filter_photo(self, src, val):
        url = None
        i = 0
        file = None
        while not url and i < len(val):
            url = val[i]['traductionFichiers'][0]['url']
        if url:
            url = self.base_url + url
            parsed_url = urlparse(url)

            if (parsed_url.scheme in ('http', 'https') and self.download_attachments) or parsed_url.scheme == 'ftp':
                content = self.download_attachment(url)
                if content is not None:
                    f = ContentFile(content)
                    basename, ext = os.path.splitext(os.path.basename(url))
                    name = '%s%s' % (basename[:128], ext)
                    file = UploadedFile(f, name=name)
                    if file and self.obj.photo:
                        if os.path.exists(self.obj.photo.path):
                            os.remove(self.obj.photo.path)
        return file

    def filter_street(self, src, val):
        return val[0]

    def filter_postal_code(self, src, val):
        return str(val)

    def filter_municipality(self, src, val):
        return str(val)

    def filter_phone(self, src, val):
        tel = self._filter_comm(val, 201, multiple=True)
        return str(tel)

    def filter_email(self, src, val):
        return self._filter_comm(val, 204, multiple=False)

    def filter_website(self, src, val):
        return self._filter_comm(val, 205, multiple=False)


class TouristicEventApidaeParser(AttachmentApidaeParserMixin, ApidaeParser):
    """Parser to import touristic events from APIDAE"""
    type = None
    themes = None
    source = None
    portal = None
    model = TouristicEvent
    fields = {
        'description_teaser': 'presentation.descriptifCourt.libelleFr',
        'description': 'presentation.descriptifDetaille.libelleFr',
        'geom': 'localisation.geolocalisation.geoJson.coordinates',
        'begin_date': 'ouverture.periodesOuvertures.0.dateDebut',
        'end_date': 'ouverture.periodesOuvertures.0.dateFin',
        'duration': ('ouverture.periodesOuvertures.0.horaireOuverture',
                     'ouverture.periodesOuvertures.-1.horaireFermeture'),
        'start_time': 'ouverture.periodesOuvertures.0.horaireOuverture',
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
        'type': 'informationsFeteEtManifestation.typesManifestation.0.libelleFr',
        'capacity': 'informationsFeteEtManifestation.nbParticipantsAttendu',
        'practical_info': (
            'ouverture.periodeEnClair.libelleFr',
            'informationsFeteEtManifestation.nbParticipantsAttendu',
            'descriptionTarif.tarifsEnClair.libelleFr',
            'descriptionTarif.modesPaiement',
            'prestations.services',
            'prestations.languesParlees',
            'localisation.geolocalisation.complement.libelleFr',
            'gestion.dateModification',
            'gestion.membreProprietaire.nom',
        ),
        'eid': 'id',
        'name': 'nom.libelleFr',
    }
    responseFields = [
        'id',
        'nom',
        'ouverture.periodeEnClair',
        'ouverture.periodesOuvertures',
        'informationsFeteEtManifestation',
        'presentation.descriptifCourt',
        'presentation.descriptifDetaille',
        'localisation.adresse',
        'localisation.geolocalisation.geoJson.coordinates',
        'localisation.geolocalisation.complement.libelleFr',
        'informations.moyensCommunication',
        'informations.structureGestion.nom.libelleFr',
        'descriptionTarif.tarifsEnClair',
        'descriptionTarif.modesPaiement',
        'prestations',
        'gestion.dateModification',
        'gestion.membreProprietaire.nom',
        'illustrations'
    ]
    m2m_fields = {
        'themes': 'informationsFeteEtManifestation.themes.*.libelleFr',
        'organizers': ('informations.structureGestion.nom.libelleFr',),
    }
    natural_keys = {
        'themes': 'label',
        'type': 'type',
        'organizers': 'label',
        'source': 'name',
        'portal': 'name',
    }
    # separator = ","

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constant_fields = self.constant_fields.copy()
        self.m2m_constant_fields = self.m2m_constant_fields.copy()
        self.field_options = self.field_options.copy()
        self.field_options['themes'] = {'create': True}
        self.field_options['type'] = {'create': True}
        self.field_options['organizers'] = {'create': True}
        if self.type is not None:
            self.constant_fields['type'] = self.type
        if self.themes is not None:
            self.m2m_constant_fields['themes'] = self.themes
        if self.source is not None:
            self.m2m_constant_fields['source'] = self.source
        if self.portal is not None:
            self.m2m_constant_fields['portal'] = self.portal

    def filter_description_teaser(self, src, val):
        return '<br>'.join(val.splitlines())

    def filter_description(self, src, val):
        return '<br>'.join(val.splitlines())

    def filter_duration(self, src, val):
        begin, end = val
        try:
            date_begin = datetime.datetime.strptime(begin, '%H:%M:%S')
            date_fin = datetime.datetime.strptime(end, '%H:%M:%S')
            return str(date_fin - date_begin)
        except TypeError:
            return None

    def filter_contact(self, src, val):
        (address1, address2, address3, zipCode, commune, comm) = val
        tel = self._filter_comm(comm, 201, multiple=True)
        if tel:
            tel = "Tél. " + tel
        lines = [line for line in [
            address1,
            address2,
            address3,
            ' '.join([part for part in [zipCode, commune] if part]),
            tel,
        ] if line]
        return '<br>'.join(lines)

    def filter_capacity(self, src, val):
        if isinstance(val, int):
            return val
        if val.isnumeric():
            return int(val)
        else:
            self.add_warning(f"Field {src} can't populate capacity field value: '{val}' isn't numeric")
            return None

    def filter_email(self, src, val):
        return self._filter_comm(val, 204, multiple=False)

    def filter_website(self, src, val):
        return self._filter_comm(val, 205, multiple=False)

    def filter_practical_info(self, src, val):
        (ouverture, capacite, tarifs, paiement, services, langues, localisation, datemodif, proprio) = val
        if ouverture:
            ouverture = "<b>Ouverture:</b><br>" + "<br>".join(ouverture.splitlines()) + "<br>"
        if capacite:
            capacite = "<b>Capacité totale:</b><br>" + str(capacite) + "<br>"
        if tarifs:
            tarifs = "<b>Tarifs:</b><br>" + "<br>".join(tarifs.splitlines()) + "<br>"
        if paiement:
            paiement = "<b>Modes de paiement:</b><br>" + ", ".join([i['libelleFr'] for i in paiement]) + "<br>"
        if services:
            services = "<b>Services:</b><br>" + ", ".join([i['libelleFr'] for i in services]) + "<br>"
        if langues:
            langues = "<b>Langues Parlées:</b><br>" + ", ".join([i['libelleFr'] for i in langues]) + "<br>"
        if localisation:
            localisation = "<b>Accès:</b><br>" + "<br>".join(localisation.splitlines()) + "<br>"
        datemodif = datetime.datetime.strptime(datemodif[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        modif = "<i>Fiche mise à jour par " + proprio + " le " + datemodif + "</i>"
        lines = [line for line in [
            ouverture,
            capacite,
            tarifs,
            paiement,
            services,
            langues,
            localisation,
            modif,
        ] if line]
        return '<br>'.join(lines)


class TouristicContentApidaeParser(AttachmentApidaeParserMixin, TouristicContentMixin, ApidaeParser):
    """Parser to import touristic contents from APIDAE"""
    separator = None
    api_key = None
    project_id = None
    selection_id = None
    category = None
    type1 = None
    type2 = None
    source = None
    portal = None
    themes = None
    url = 'http://api.apidae-tourisme.com/api/v002/recherche/list-objets-touristiques/'
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
    natural_keys = {
        'themes': 'label',
        'category': 'label',
        'type1': 'label',
        'type2': 'label',
        'source': 'name',
        'portal': 'name',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constant_fields = self.constant_fields.copy()
        self.m2m_constant_fields = self.m2m_constant_fields.copy()
        if self.category:
            self.constant_fields['category'] = self.category
        if self.type1 is not None:
            self.m2m_constant_fields['type1'] = self.type1
        if self.type2 is not None:
            self.m2m_constant_fields['type2'] = self.type2
        if self.themes is not None:
            self.m2m_constant_fields['themes'] = self.themes
        if self.source is not None:
            self.m2m_constant_fields['source'] = self.source
        if self.portal is not None:
            self.m2m_constant_fields['portal'] = self.portal

    def filter_email(self, src, val):
        return self._filter_comm(val, 204, multiple=False)

    def filter_website(self, src, val):
        return self._filter_comm(val, 205, multiple=False)

    def filter_contact(self, src, val):
        (address1, address2, address3, zipCode, commune, comm) = val
        tel = self._filter_comm(comm, 201, multiple=True)
        if tel:
            tel = "Tél. " + tel
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
            ouverture = "<b>Ouverture:</b><br>" + "<br>".join(ouverture.splitlines()) + "<br>"
        if capacite:
            capacite = "<b>Capacité totale:</b><br>" + str(capacite) + "<br>"
        if tarifs:
            tarifs = "<b>Tarifs:</b><br>" + "<br>".join(tarifs.splitlines()) + "<br>"
        if paiement:
            paiement = "<b>Modes de paiement:</b><br>" + ", ".join([i['libelleFr'] for i in paiement]) + "<br>"
        if services:
            services = "<b>Services:</b><br>" + ", ".join([i['libelleFr'] for i in services]) + "<br>"
        if localisation:
            localisation = "<b>Accès:</b><br>" + "<br>".join(localisation.splitlines()) + "<br>"
        datemodif = datetime.datetime.strptime(datemodif[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        modif = "<i>Fiche mise à jour par " + proprio + " le " + datemodif + "</i>"
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


class HebergementsApidaeParser(TouristicContentApidaeParser):
    category = "Hébergements"
    m2m_fields = {
        'type1': 'informationsHebergementCollectif.hebergementCollectifType.libelleFr',
    }

    def filter_type1(self, src, val):
        return self.apply_filter('type1', src, [val])


class EspritParcParser(AttachmentParserMixin, TouristicContentMixin, Parser):
    model = TouristicContent
    eid = 'eid'
    separator = None
    delete = True
    fields = {
        'eid': 'eid',
        'name': 'nomCommercial',
        'description': 'descriptionDetaillee',
        'practical_info': 'informationsPratiques',
        'category': 'type.label',
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
        'type1': 'sousType.label',
        'type2': 'classement',
    }

    non_fields = {
        'attachments': 'photo',
    }

    def filter_attachments(self, src, val):
        result = []
        for subval in val or []:
            if 'url' in subval:
                result.append((subval['url'],
                               subval.get('legende', None),
                               subval.get('credits', None)))
        return result

    @property
    def items(self):
        return self.root['responseData'] or []

    def next_row(self):
        response = self.request_or_retry(self.url)
        self.root = response.json()
        self.nb = int(self.root['numFound'])

        for row in self.items:
            yield row

    def normalize_field_name(self, name):
        return name

    def filter_eid(self, src, val):
        return "{}".format(val)

    def filter_contact(self, src, val):
        (address, zipCode, commune, telephone, gsm, fax, facebook, twitter) = val
        cp_com = ' '.join([part for part in (zipCode, commune) if part])
        return '<br>'.join([part for part in (address, cp_com, telephone, gsm, fax, facebook, twitter) if part])

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
        if val:
            if isinstance(val, str):
                val = [val]
            for subval in val:
                try:
                    dst.append(TouristicContentType1.objects.get(category=self.obj.category, label=subval))
                except TouristicContentType1.DoesNotExist:
                    self.add_warning(
                        _("Type 1 '{subval}' does not exist for category '{cat}'. Please add it").format(
                            subval=subval, cat=self.obj.category.label))
        return dst

    def filter_type2(self, src, val):
        dst = []
        if val:
            if isinstance(val, str):
                val = [val]
            for subval in val:
                try:
                    dst.append(TouristicContentType2.objects.get(category=self.obj.category, label=subval))
                except TouristicContentType2.DoesNotExist:
                    self.add_warning(
                        _("Type 2 '{subval}' does not exist for category '{cat}'. Please add it").format(
                            subval=subval, cat=self.obj.category.label))
        return dst


# Deprecated: for compatibility only
TouristicContentSitraParser = TouristicContentApidaeParser
HebergementsSitraParser = HebergementsApidaeParser


class TouristicContentTourInSoftParser(TouristicContentMixin, TourInSoftParser):
    eid = 'eid'
    model = TouristicContent
    delete = True
    category = None
    type1 = None
    type2 = None
    themes = None
    source = None
    portal = None

    constant_fields = {
        'published': True,
        'deleted': False,
    }

    fields = {
        'eid': 'SyndicObjectID',
        'name': 'SyndicObjectName',
        'description_teaser': 'DescriptionCommerciale',
        'geom': ('GmapLongitude', 'GmapLatitude'),
        'practical_info': (
            'LanguesParlees',
            'PeriodeOuverture',
            'PrestationsEquipements',
        ),
        'contact': ('MoyenDeCom', 'AdresseComplete'),
        'email': 'MoyenDeCom',
        'website': 'MoyenDeCom',
    }

    non_fields = {
        'attachments': 'Photos',
    }

    field_options = {
        'geom': {'required': True},
        'type1': {'create': True, 'fk': 'category'},
        'type2': {'create': True, 'fk': 'category'},
    }

    natural_keys = {
        'category': 'label',
        'type1': 'label',
        'type2': 'label',
        'source': 'name',
        'portal': 'name',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constant_fields = self.constant_fields.copy()
        self.m2m_constant_fields = self.m2m_constant_fields.copy()
        if self.category:
            self.constant_fields['category'] = self.category
        if self.type1 is not None:
            self.m2m_constant_fields['type1'] = self.type1
        if self.type2 is not None:
            self.m2m_constant_fields['type2'] = self.type2
        if self.themes is not None:
            self.m2m_constant_fields['themes'] = self.themes
        if self.source is not None:
            self.m2m_constant_fields['source'] = self.source
        if self.portal is not None:
            self.m2m_constant_fields['portal'] = self.portal

    def filter_practical_info(self, src, val):
        langues, periodes, equipements = val
        infos = []

        if langues:
            infos.append(
                "<strong>Langues parlées :</strong><br>"
                + "<br>".join(langues.split(self.separator))
            )

        if periodes:
            periode_infos = ["<strong>Période d'ouverture :</strong>"]
            for periode in periodes.split(self.separator):
                items = periode.split(self.separator2)
                if len(items) >= 2 and items[0] and items[1]:
                    periode_infos.append(
                        "du %s au %s" % (items[0], items[1])
                    )
            infos.append("<br>".join(periode_infos))

        if equipements:
            infos.append(
                "<strong>Équipements :</strong><br>"
                + "<br>".join(equipements.split(self.separator))
            )

        return "<br><br>".join(infos)


class TouristicContentTourInSoftParserV3(TouristicContentTourInSoftParser):
    version_tourinsoft = 3


class TouristicContentTourInSoftParserV3withMedias(TouristicContentTourInSoftParserV3):

    non_fields = {
        'attachments': 'MediaPhotoss',
    }

    def get_nb(self):
        return int(len(self.root['value']))

    def filter_attachments(self, src, val):
        if not val:
            return []
        else:
            return [
                (entry["Photo"]["Url"], entry["Photo"]["Titre"], entry["Photo"]["Credit"])
                for entry in val if entry["Photo"] is not None
            ]


class TouristicEventTourInSoftParser(TourInSoftParser):
    eid = 'eid'
    model = TouristicEvent
    delete = True
    type = None
    themes = None
    source = None
    portal = None

    constant_fields = {
        'published': True,
        'deleted': False,
    }

    fields = {
        'eid': 'SyndicObjectID',
        'name': 'SyndicObjectName',
        'description': 'DescriptionCommerciale2',
        'description_teaser': 'DescriptionCommerciale',
        'geom': ('GmapLongitude', 'GmapLatitude'),
        'practical_info': (
            'LanguesParlees',
            'PrestationsEquipements',
        ),
        'contact': ('MoyenDeCom', 'AdresseComplete'),
        'email': 'MoyenDeCom',
        'website': 'MoyenDeCom',
        'begin_date': 'PeriodeOuverture',
        'end_date': 'PeriodeOuverture'
    }

    non_fields = {
        'attachments': 'Photos',
    }

    field_options = {
        'geom': {'required': True},
    }

    natural_keys = {
        'type': 'type',
        'source': 'name',
        'portal': 'name',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.constant_fields = self.constant_fields.copy()
        self.m2m_constant_fields = self.m2m_constant_fields.copy()
        if self.type is not None:
            self.constant_fields['type'] = self.type
        if self.themes is not None:
            self.m2m_constant_fields['themes'] = self.themes
        if self.source is not None:
            self.m2m_constant_fields['source'] = self.source
        if self.portal is not None:
            self.m2m_constant_fields['portal'] = self.portal

    def filter_practical_info(self, src, val):
        langues, equipements = val
        infos = []

        if langues:
            infos.append(
                "<strong>Langues parlées :</strong><br>"
                + "<br>".join(langues.split(self.separator))
            )

        if equipements:
            infos.append(
                "<strong>Équipements :</strong><br>"
                + "<br>".join(equipements.split(self.separator))
            )

        return "<br><br>".join(infos)

    def filter_begin_date(self, src, val):
        if val:
            for subval in val.split(self.separator):
                values = subval.split(self.separator2)
                if values and values[1]:
                    day, month, year = values[1].split('/')
                    if datetime.date(int(year), int(month), int(day)) < datetime.date.today():
                        continue
                if values and values[0]:
                    day, month, year = values[0].split('/')
                    return '{year}-{month}-{day}'.format(year=year, month=month, day=day)

    def filter_end_date(self, src, val):
        if val:
            for subval in val.split(self.separator):
                values = subval.split(self.separator2)
                if values and values[1]:
                    day, month, year = values[1].split('/')
                    if datetime.date(int(year), int(month), int(day)) < datetime.date.today():
                        continue
                    return '{year}-{month}-{day}'.format(year=year, month=month, day=day)


class TouristicEventTourInSoftParserV3(TouristicEventTourInSoftParser):
    version_tourinsoft = 3


class LEITouristicContentParser(LEIParser):
    """LEI Parser for Touristic contents"""
    model = TouristicContent
    eid = 'eid'
    delete = True
    category = None
    type1 = None
    type2 = None
    practical_info = []
    fields = {
        'eid': 'PRODUIT',
        'name': 'NOM',
        'description': 'COMMENTAIRE',
        'contact': ('ADRPROD_NUM_VOIE', 'ADRPROD_LIB_VOIE', 'ADRPROD_CP', 'ADRPROD_LIBELLE_COMMUNE',
                    'ADRPROD_TEL', 'ADRPROD_TEL2', 'ADRPREST_TEL', 'ADRPREST_TEL2'),
        'email': ('ADRPROD_EMAIL', 'ADRPREST_EMAIL', 'ADRPREST_EMAIL2'),
        'website': ('ADRPROD_URL', 'ADRPREST_URL'),
        'geom': ('LATITUDE', 'LONGITUDE'),
    }

    field_options = {
        'geom': {'required': True},
        'type1': {'create': True, 'fk': 'category'},
        'type2': {'create': True, 'fk': 'category'},
    }

    constant_fields = {
        'published': True,
    }
    natural_keys = {
        'category': 'label',
        'type1': 'label',
        'type2': 'label',
    }
    m2m_fields = {}
    m2m_constant_fields = {}
    non_fields = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.category:
            self.constant_fields['category'] = self.category
        if self.type1 is not None:
            self.m2m_fields['type1'] = self.type1
        if self.type2 is not None:
            self.m2m_fields['type2'] = self.type2
        if self.practical_info is not None:
            self.fields['practical_info'] = self.practical_info


class LEITouristicEventParser(LEIParser):
    """LEI Parser for touristic events"""
    model = TouristicEvent
    fields = {
        'eid': 'PRODUIT',
        'name': 'NOM',
        'description': 'COMMENTAIRE',
        'description_teaser': 'COMMENTAIREL1',
        'begin_date': 'PERIODE_DU',
        'end_date': 'PERIODE_AU',
        'duration': ('PERIODE_DU', 'PERIODE_AU'),
        'contact': ('ADRPROD_NUM_VOIE', 'ADRPROD_LIB_VOIE', 'ADRPROD_CP', 'ADRPROD_LIBELLE_COMMUNE',
                    'ADRPROD_TEL', 'ADRPROD_TEL2', 'ADRPREST_TEL', 'ADRPREST_TEL2'),
        'email': ('ADRPROD_EMAIL', 'ADRPREST_EMAIL', 'ADRPREST_EMAIL2'),
        'website': ('ADRPROD_URL', 'ADRPREST_URL'),
        'speaker': ('CIVILITE_RESPONSABLE', 'NOM_RESPONSABLE', 'PRENOM_RESPONSABLE'),
        'type': 'TYPE_NOM',
        'geom': ('LATITUDE', 'LONGITUDE'),
    }
    m2m_fields = {
        'organizers': ('RAISONSOC_PERSONNE_EN_CHARGE', 'RAISONSOC_RESPONSABLE')
    }
    type = None
    natural_keys = {
        'category': 'label',
        'organizers': 'label',
        'geom': {'required': True},
        'type': 'type',
    }
    constant_fields = {}
    m2m_constant_fields = {}
    non_fields = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field_options['organizers'] = {'create': True}
        if self.type:
            self.constant_fields['type'] = self.type

    def filter_description_teaser(self, src, val):
        if val:
            val = val.replace('\n', '<br>')
        return val

    def filter_organizers(self, src, val):
        (first, second) = val
        return self.apply_filter('organizers', src, [first if first else second])

    def filter_speaker(self, src, val):
        (civilite, nom, prenom) = val
        return "{civ} {pre} {nom}".format(civ=civilite, pre=prenom, nom=nom)

    def filter_begin_date(self, src, val):
        values_tab = val.split('/')
        return '-'.join(values_tab[::-1])

    def filter_end_date(self, src, val):
        values_tab = val.split('/')
        return '-'.join(values_tab[::-1])

    def filter_duration(self, src, val):
        (debut, fin) = val
        date_y_m_d_begin = debut.split('/')
        date_y_m_d_end = fin.split('/')
        d0 = datetime.date(int(date_y_m_d_begin[2]), int(date_y_m_d_begin[1]), int(date_y_m_d_begin[0]))
        d1 = datetime.date(int(date_y_m_d_end[2]), int(date_y_m_d_end[1]), int(date_y_m_d_end[0]))
        delta = d1 - d0
        return str(delta.days + 1)


class GeotrekTouristicContentParser(GeotrekParser):
    """Geotrek parser for TouristicContent"""
    fill_empty_translated_fields = True
    url = None
    model = TouristicContent
    constant_fields = {
        'deleted': False,
    }

    replace_fields = {
        "eid": "uuid",
        "geom": "geometry",
    }

    m2m_replace_fields = {
        "type1": "types",
        "type2": "types"
    }

    url_categories = {
        "structure": "structure",
        "category": "touristiccontent_category",
        "themes": "theme",
        "source": "source"
    }

    categories_keys_api_v2 = {
        "structure": "name",
        'category': 'label',
        'themes': 'label',
        'source': 'name'
    }

    natural_keys = {
        "structure": "name",
        'category': 'label',
        'themes': 'label',
        'type1': 'label',
        'type2': 'label',
        'source': 'name'
    }

    field_options = {
        'type1': {'fk': 'category'},
        'type2': {'fk': 'category'},
        'geom': {'required': True},
    }

    def __init__(self, *args, **kwargs):
        """Initialize parser with mapping for type1 and type2"""
        super().__init__(*args, **kwargs)
        response = self.request_or_retry(f"{self.url}/api/v2/touristiccontent_category/", )
        self.field_options.setdefault("type1", {})
        self.field_options.setdefault("type2", {})
        self.field_options["type1"]["mapping"] = {}
        self.field_options["type2"]["mapping"] = {}
        for r in response.json()['results']:
            for type_category in r['types']:
                values = type_category["values"]
                id_category = type_category["id"]
                if self.create_categories:
                    self.field_options['type1']["create"] = True
                    self.field_options['type2']["create"] = True
                for value in values:
                    if id_category % 10 == 1:
                        self.field_options['type1']["mapping"][value['id']] = self.replace_mapping(
                            value['label'][settings.MODELTRANSLATION_DEFAULT_LANGUAGE], 'type1'
                        )
                    if id_category % 10 == 2:
                        self.field_options['type2']["mapping"][value['id']] = self.replace_mapping(
                            value['label'][settings.MODELTRANSLATION_DEFAULT_LANGUAGE], 'type2'
                        )
        self.next_url = f"{self.url}/api/v2/touristiccontent"

    def filter_type1(self, src, val):
        type1_result = []
        for key, value in val.items():
            if int(key) % 10 == 1:
                type1_result.extend(value)
        return self.apply_filter('type1', src, type1_result)

    def filter_type2(self, src, val):
        type2_result = []
        for key, value in val.items():
            if int(key) % 10 == 2:
                type2_result.extend(value)
        return self.apply_filter('type2', src, type2_result)


class GeotrekTouristicEventParser(GeotrekParser):
    """Geotrek parser for TouristicEvent"""
    fill_empty_translated_fields = True
    url = None
    model = TouristicEvent
    constant_fields = {
        'deleted': False,
    }
    replace_fields = {
        "eid": "uuid",
        "geom": "geometry"
    }
    url_categories = {
        "structure": "structure",
        "type": "touristicevent_type",
        "source": "source"
    }
    categories_keys_api_v2 = {
        "structure": "name",
        'type': 'type',
        'source': 'name'
    }
    natural_keys = {
        "structure": "name",
        'type': 'type',
        'source': 'name'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/touristicevent"


class GeotrekInformationDeskParser(GeotrekParser):
    """Geotrek parser for InformationDesk"""
    fill_empty_translated_fields = True
    url = None
    model = InformationDesk
    constant_fields = {}
    replace_fields = {
        "eid": "uuid",
        "geom": ["latitude", "longitude"],
        "photo": "photo_url"
    }
    url_categories = {}
    categories_keys_api_v2 = {}
    natural_keys = {
        'type': 'label',
    }

    field_options = {
        "type": {"create": True},
        'geom': {'required': True},
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/informationdesk"

    def filter_geom(self, src, val):
        lat, lng = val
        return Point(lng, lat, srid=settings.API_SRID).transform(settings.SRID, clone=True)

    def filter_type(self, src, val):
        return self.apply_filter('type', src, val["label"][settings.MODELTRANSLATION_DEFAULT_LANGUAGE])

    def filter_photo(self, src, val):
        if not val:
            return None
        content = self.download_attachment(val)
        if content is None:
            return None
        f = ContentFile(content)
        basename, ext = os.path.splitext(os.path.basename(val))
        name = '%s%s' % (basename[:128], ext)
        file = UploadedFile(f, name=name)
        return file

    def link_informationdesks(self, parser, datas, match_id_uuid, json_uuid_key):
        model_imported = parser.model
        field = "information_desks"
        for row in datas['results']:
            try:
                trek = model_imported.objects.get(**{json_uuid_key: row[json_uuid_key]})
            except Trek.DoesNotExist:
                self.add_warning(_("Cannot link information desk to trek: could not find "
                                   "trek with UUID %(uuid)s") % {"uuid": row[json_uuid_key]})
            else:
                infodesks_to_set = [match_id_uuid.get(val) for val in row[field]
                                    if match_id_uuid.get(val)]
                # object_result_field is the objects found for each field in initial_fields
                # example every information desks for one trek
                current_infodesks = getattr(trek, field)
                infodesks_to_remove = current_infodesks.exclude(
                    id__in=[object_result.pk for object_result in infodesks_to_set])
                if infodesks_to_remove:
                    current_infodesks.remove(
                        *infodesks_to_remove
                    )
                getattr(trek, field).add(*infodesks_to_set)

    def end_meta(self):
        super().end_meta()
        url = f"{self.url}/api/v2/informationdesk"
        params = self.params_used
        replace_fields = self.replace_fields
        fields = f"{replace_fields.get('eid', 'uuid')},id"
        params['fields'] = fields
        params['page_size'] = 10000

        response = self.request_or_retry(url, params=params)
        datas = response.json()
        match_id_uuid = {}
        for result in datas['results']:
            try:
                match_id_uuid[result['id']] = InformationDesk.objects.get(uuid=result['uuid'])
            except InformationDesk.DoesNotExist:
                pass

        url = f"{self.url}/api/v2/trek"
        params = self.params_used
        replace_fields = GeotrekTrekParser.replace_fields
        fields = f"{replace_fields.get('eid', 'id')},information_desks"
        params['fields'] = fields
        params['page_size'] = 10000
        response = self.request_or_retry(url, params=params)
        datas = response.json()
        self.link_informationdesks(GeotrekTrekParser, datas, match_id_uuid, replace_fields.get('eid', 'id'))


class InformationDeskOpenStreetMapParser(OpenStreetMapParser):
    """Parser to import information desks from OpenStreetMap"""
    type = None
    model = InformationDesk
    fields = {
        'eid': 'id',
        'phone': ("tags.contact:phone", "tags.phone"),
        'email': ("tags.contact:email", "tags.email"),
        'website': ("tags.contact:website", "tags.website"),
        'street': ("tags.addr:housenumber", "tags.addr:street"),
        'postal_code': ("tags.addr:postcode", "tags.contact:postcode"),
        'municipality': ("tags.addr:city", "tags.contact:city"),
        'geom': ('type', 'lon', 'lat', 'geometry', 'bounds'),
        'name': 'tags.name',
    }
    constant_fields = {}
    natural_keys = {
        'type': 'label',
    }
    non_fields = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.type:
            self.constant_fields['type'] = self.type

    def filter_street(self, src, val):
        housenumber, street = val
        if housenumber and street:
            return housenumber + " " + street
        elif street:
            return street
        return None

    def filter_postal_code(self, src, val):
        return self.get_tag_info(val)

    def filter_municipality(self, src, val):
        return self.get_tag_info(val)

    def filter_phone(self, src, val):
        return self.get_tag_info(val)

    def filter_email(self, src, val):
        return self.get_tag_info(val)

    def filter_website(self, src, val):
        return self.get_tag_info(val)

    def filter_geom(self, src, val):
        type, lng, lat, area, bbox = val
        if type == "node":
            geom = Point(float(lng), float(lat), srid=4326)  # WGS84
            geom.transform(settings.SRID)
            return geom
        elif type == "way":
            return self.get_centroid_from_way(area)
        elif type == "relation":
            return self.get_centroid_from_relation(bbox)