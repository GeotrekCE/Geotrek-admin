# -*- encoding: utf-8 -*-

from django.conf import settings
from django.contrib.gis.geos import Point
from geotrek.common.parsers import TourismSystemParser, RowImportError
from geotrek.tourism.models import TouristicContent


class CrtCaParser(TourismSystemParser):
    model = TouristicContent
    user = 'makina_guest'
    password = 'e976946a'
    eid = 'eid'
    fields = {
        'eid': 'data.idFiche',
        'name': 'data.dublinCore.title',
        'description_fr': 'data.dublinCore.description.fr',
        'description_en': 'data.dublinCore.description.en',
        'description_de': 'data.dublinCore.description.de',
        'description_nl': 'data.dublinCore.description.nl',
        'contact': ('data.contacts.0.addresses.0.address1',
                    'data.contacts.0.addresses.0.address2',
                    'data.contacts.0.addresses.0.zipCode',
                    'data.contacts.0.addresses.0.commune',
                    'data.contacts.0.addresses.0.people.0.communicationMeans'),
        'email': 'data.contacts.0.addresses.0.people.0.communicationMeans',
        'website': 'data.contacts.0.addresses.0.people.0.communicationMeans',
        'geom': ('data.geolocations.0.zone.0.points.0.coordinates.0.latitude',
                 'data.geolocations.0.zone.0.points.0.coordinates.0.longitude'),
        # tel ?
    }
    constant_fields = {
        'published_{lang}'.format(lang=lang): True for lang in settings.MODELTRANSLATION_LANGUAGES
    }
    non_fields = {
        'attachments': 'data.multimedia',
    }
    natural_keys = {
        'category': 'label',
        'type1': 'label',
    }

    def filter_contact(self, src, val):
        (address1, address2, zipCode, commune, comm) = val
        tel = self.filter_comm(comm, '04.02.01')
        if tel:
            tel = u"Tél. " + tel
        lines = [line for line in [
            address1,
            address2,
            ' '.join([part for part in [zipCode, commune] if part]),
            tel,
        ] if line]
        return '<br>'.join(lines)

    def filter_comm(self, val, code):
        if not val:
            return None
        for subval in val:
            if subval['type'] == code:
                return subval.get('particular')

    def filter_email(self, src, val):
        return self.filter_comm(val, '04.02.04')

    def filter_website(self, src, val):
        return self.filter_comm(val, '04.02.05')

    def filter_geom(self, src, val):
        lat, lng = val
        if lng == '' or lat == '':
            raise RowImportError(u"Required value for fields 'GmapLatitude' and 'GmapLongitude'.")
        geom = Point(float(lng), float(lat), srid=4326)  # WGS84
        geom.transform(settings.SRID)
        return geom


class CampingsParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/cf13d57fe1f8469650a9b55778d6ec50'
    constant_fields = dict(
        category=u"Dormir",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Campings",
    }


class BnBParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/89dd60f992bd168e8040de2f9745ad28'
    constant_fields = dict(
        category=u"Dormir",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Chambres d’hôtes",
    }


class GitesEtMeublesParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/4620d1a25a922c6a5db6dd47aab199e4'
    constant_fields = dict(
        category=u"Dormir",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Gîtes et meublés",
    }


class HebergementsCollectifsParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/c6713b855b63f97a80c4927c16583dd7'
    constant_fields = dict(
        category=u"Dormir",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Hébergements collectifs",
    }


class HotelsParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/c302f808b0f119c27e6a9472381e724f'
    constant_fields = dict(
        category=u"Dormir",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Hôtels",
    }


class CampingCarsParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/d2f0d36e64e5d018514adf1dfacd0f9f'
    constant_fields = dict(
        category=u"Dormir",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Camping-cars",
    }


class RestaurantsParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/97fdf3a93ce040fd14e0ac314a604ff8'
    constant_fields = dict(
        category=u"Manger",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Restaurants",
    }


class SitesDeVisiteParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/026e124ece77463f9c052cb8c8077fc8'
    constant_fields = dict(
        category=u"Visiter",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Sites de visite",
    }


class PointsDeVueParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/e9f995c532aa031daff70f33468dd97c'
    constant_fields = dict(
        category=u"Visiter",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Points de vue",
    }


class SitesPedagogiquesParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/10e9ce7d5a13f34ce722fcf724bebfad'
    constant_fields = dict(
        category=u"Visiter",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Sites pédagogiques",
    }


class ArtisanatParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/c5f0058d1b99f35105590edfbf20f373'
    constant_fields = dict(
        category=u"A faire",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Artisanat et savoirs faire",
    }


class ActivitesParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/e26c7e16eadd51044779a9687ac7672e'
    constant_fields = dict(
        category=u"A faire",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Activités (bouger)",
    }


class CavesParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/5152cd98a69aef5e4477a0802ce47fb6'
    constant_fields = dict(
        category=u"Déguster",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Caves",
    }


class ProduitsParser(CrtCaParser):
    url = 'http://api.tourism-system.com/content/ts/champagneardenne_v2/1a0cb871e5c148ffd8e1185f24cbe1d4'
    constant_fields = dict(
        category=u"Déguster",
        **CrtCaParser.constant_fields
    )
    m2m_constant_fields = {
        'type1': u"Produits du terroir",
    }
