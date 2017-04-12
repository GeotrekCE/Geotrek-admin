# -*- encoding: utf-8 -*-

import requests
import xml.etree.ElementTree as ET
from django.conf import settings
from django.contrib.gis.geos import Point
from django.db import InternalError
from geotrek.common.parsers import Parser, AttachmentParserMixin, ValueImportError, GlobalImportError, RowImportError
from geotrek.tourism.models import TouristicContent


class XmlParser(Parser):
    ns = {}
    root = ''

    def get_part(self, dst, src, val):
        return val.findtext(src, None, self.ns)

    def next_row(self):
        if self.filename:
            with open(self.filename) as f:
                tree = ET.fromstring(f.read())
        else:
            response = requests.get(self.url, params={})
            if response.status_code != 200:
                raise GlobalImportError(_(u"Failed to download {url}. HTTP status code {status_code}").format(url=self.url, status_code=response.status_code))
            tree = ET.fromstring(response.content)
        entries = tree.findall(self.root, self.ns)
        self.nb = len(entries)
        for entry in entries:
            yield entry

    def normalize_field_name(self, name):
        return name


class LeiParser(AttachmentParserMixin, XmlParser):
    root = 'Resultat/sit_liste'
    model = TouristicContent
    eid = 'eid'
    delete = True
    fields = {
        'eid': 'PRODUIT',
        'name': 'NOM',
        'description': 'COMMENTAIRE',
        'contact': ('ADRPROD_NUM_VOIE', 'ADRPROD_LIB_VOIE', 'ADRPROD_CP', 'ADRPROD_LIBELLE_COMMUNE', 'ADRPROD_TEL'),
        'email': 'ADRPROD_EMAIL',
        'website': 'ADRPROD_URL',
        'geom': ('LATITUDE', 'LONGITUDE'),
    }
    category = None
    type1 = None
    non_fields = {
        'attachments': ('CRITERES/Crit[@CLEF_CRITERE="1900421"]', 'CRITERES/Crit[@CLEF_CRITERE="1900480"]'),
    }
    constant_fields = {
        'published': True,
    }
    natural_keys = {
        'category': 'label',
    }

    def __init__(self, *args, **kwargs):
        XmlParser.__init__(self, *args, **kwargs)
        if self.category:
            self.constant_fields['category'] = self.category
        if self.type1:
            self.constant_fields['type1'] = self.type1

    def start(self):
        super(LeiParser, self).start()
        lei = set(self.model.objects.filter(eid__startswith='LEI').values_list('pk', flat=True))
        self.to_delete = self.to_delete & lei

    def filter_eid(self, src, val):
        return 'LEI' + val

    def filter_attachments(self, src, val):
        (url, legend) = val
        if not url:
            return []
        if url[:7] != 'http://':
            url = 'http://' + url
        return [(url, legend, '')]

    def filter_description(self, src, val):
        return val.replace('\n', '<br>')

    def filter_geom(self, src, val):
        lat, lng = val
        lat = lat.replace(',', '.')
        lng = lng.replace(',', '.')
        if lat is None or lng is None:
            return None
        geom = Point(float(lng), float(lat), srid=4326)  # WGS84
        try:
            geom.transform(settings.SRID)
        except InternalError as e:
            raise ValueImportError(unicode(e))
        return geom

    def filter_contact(self, src, val):
        (num, voie, cp, commune, tel) = val
        val = num or u""
        if num and voie:
            val += u" "
        val += voie or u""
        if num or voie:
            val += u"<br>"
        val += cp
        if cp and commune:
            val += u" "
        val += commune or u""
        if cp or commune:
            val += u"<br>"
        if tel:
            val += u"Tél. : " + tel
        return val

    def filter_website(self, src, val):
        if not val:
            return None
        return 'http://' + val


class LeiHebergementParser(LeiParser):
    label = u"LEI - Hébergement"
    url = 'http://apps.tourisme-alsace.info/batchs/LIENS_PERMANENTS/2002084000002_pnrvn_hebergements.xml'
    category = u"Hébergement"


class LeiActivitesParser(LeiParser):
    label = u"LEI - Activités / lieux à visiter"
    url = 'http://apps.tourisme-alsace.info/batchs/LIENS_PERMANENTS/2002084000003_pnrvn_lieux_activites.xml'
    category = u"Activités"


# class LeiCommercesParser(LeiParser):
#     label = u"LEI - Commerces et services"
#     url = 'http://apps.tourisme-alsace.info/batchs/LIENS_PERMANENTS/2002084000004_pnrvn_services_commerces.xml'
#     category = u"Commerces"


# Pour les événements
# http://apps.tourisme-alsace.info/batchs/LIENS_PERMANENTS/2002084000005_pnrvn_manifestations.xml


class SitlorParser(LeiParser):
    model = TouristicContent
    eid = 'eid'
    delete = True
    fields = {
        'eid': 'PRODUIT',
        'name': 'NOM',
        'description': 'COMMENTAIRE',
        'contact': ('ADRPROD_NUM_VOIE', 'ADRPROD_LIB_VOIE', 'ADRPROD_CP', 'ADRPROD_LIBELLE_COMMUNE', 'ADRPROD_TEL'),
        'email': 'ADRPROD_EMAIL',
        'website': 'ADRPROD_URL',
        'geom': ('LATITUDE', 'LONGITUDE'),
        'category': 'TYPE_NOM',
    }
    category = None
    type1 = None
    non_fields = {
        'attachments': 'CRITERES/Crit[@CLEF_CRITERE="736000294"]',
    }
    constant_fields = {
        'published': True,
    }
    natural_keys = {
        'category': 'label',
    }

    def __init__(self, *args, **kwargs):
        LeiParser.__init__(self, *args, **kwargs)
        if self.category:
            self.fields['category'] = self.category
        if self.type1:
            self.fields['type1'] = self.type1

    def filter_eid(self, src, val):
        return 'LOR' + val

    def filter_attachments(self, src, val):
        if not val:
            return []
        return [(val, "", "")]

    def filter_description(self, src, val):
        return val.replace('\n', '<br>')

    def filter_geom(self, src, val):
        lat, lng = val
        lat = lat.replace(',', '.')
        lng = lng.replace(',', '.')
        if lat is None or lng is None:
            return None
        geom = Point(float(lng), float(lat), srid=4326)  # WGS84
        try:
            geom.transform(settings.SRID)
        except InternalError as e:
            raise ValueImportError(unicode(e))
        return geom

    def filter_contact(self, src, val):
        (num, voie, cp, commune, tel) = val
        val = u""
        if num:
            val += num + u" "
        val += voie + u"<br>" + cp + u" " + commune + u"<br>Tél. : " + tel
        return val

    def filter_website(self, src, val):
        return 'http://' + val


# class SitlorParser(SitlorParser):
#     label = "SITLOR - Activités de loisirs"
#     url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000008,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000001'


# class SitlorParser(SitlorParser):
#     label = "SITLOR - Itinéraires touristiques"
#     url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000078,PNRVNETENDU,2000640,,+12M&PNAMES=eltypo,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000002'


# class SitlorParser(SitlorParser):
#     label = "SITLOR - Lieux de sortie"
#     url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000016,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000003'


# class SitlorParser(SitlorParser):
#     label = "SITLOR - Patrimoine culturel"
#     url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000012,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000004'


# class SitlorParser(SitlorParser):
#     label = "SITLOR - Patrimoine naturel"
#     url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000013,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000005'


class SitlorProduitsParser(SitlorParser):
    label = u"SITLOR - Produits - spécialités de terroir"
    url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000009,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000006'
    category = u"Produits"


# class SitlorParser(SitlorParser):
#     label = "SITLOR - Métiers d'art et de l'artisanat"
#     url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000069,PNRVNETENDU,2000640,,+12M&PNAMES=eltypo,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000007'


class SitlorChambresDHoteParser(SitlorParser):
    label = u"SITLOR - Chambres d'hôtes"
    url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000001,PNRVNETENDU,2000640,,+12M&PNAMES=eltypo,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000008'
    category = u"Hébergement"
    type1 = u"Chambres d'hôtes"


class SitlorHebergementCollectifParser(SitlorParser):
    label = "SITLOR - Hébergement collectif"
    url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000006,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000009'
    category = u"Hébergement"
    type1 = u"Hébergement collectif"


class SitlorHotellerieParser(SitlorParser):
    label = "SITLOR - Hôtellerie"
    url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000002,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000010'
    category = u"Hébergement"
    type1 = u"Hôtellerie"


class SitlorCampingParser(SitlorParser):
    label = "SITLOR - Hôtellerie de plein air"
    url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000003,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000011'


class SitlorMeubleParser(SitlorParser):
    label = "SITLOR - Meublé"
    url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000012,PNRVNETENDU,2000640,,+12M&PNAMES=eltypo,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000012'


class SitlorRestaurantParser(SitlorParser):
    label = "SITLOR - Restaurants"
    url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000007,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000013'


class SitlorOtParser(SitlorParser):
    label = "SITLOR - Offices du tourisme"
    url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000017,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000014'


# class SitlorParser(SitlorParser):
#     label = "SITLOR - Santé"
#     url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000027,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000015'


# class SitlorParser(SitlorParser):
#     label = "SITLOR - Transport - stationnement"
#     url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000028,PNRVNETENDU,2000640,,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000016'


# class SitlorParser(SitlorParser):
#     label = "SITLOR - Vie pratique"
#     url = 'http://www.sitlor.fr/xml/exploitation/listeproduits.asp?rfrom=1&rto=20&user=2000640&pwkey=86a9bc7359cf106c904a28bb8b5c7002&urlnames=tous&PVALUES=4000029,PNRVNETENDU,2000640,@,+12M&PNAMES=alcat,elsector,utilisador,horariodu,horarioau&tshor=Y&clause=2000640000017'
