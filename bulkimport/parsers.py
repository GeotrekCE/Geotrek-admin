# -*- encoding: utf-8 -*-

import requests

from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils.translation import ugettext as _
from geotrek.common.parsers import TourInSoftParser, RowImportError, GlobalImportError
from geotrek.tourism.models import TouristicContent, TouristicEvent


class NormandieMainParser(TourInSoftParser):
    delete_attachments = True
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/b169bd47-3cc3-4b2a-ba7f-92b448107e0c/Objects'
    model = TouristicContent
    eid = 'eid'
    constant_fields = {
        'category': u"Hébergement",
        'published': True,
    }
    natural_keys = {
        'category': 'label',
        'type1': 'label',
        'type2': 'label',
    }
    non_fields = {
        'attachments': 'Photos',
    }

    def filter_attachments(self, src, val):
        if not val:
            return []
        return [subval.split('|') for subval in val.split('#') if subval.split('|')[0]]

    def filter_contact(self, src, val):
        (Adresse1, Adresse1Suite, Adresse2, Adresse3, CodePostal, Commune, Cedex) = val
        lines = [line for line in [
            ' '.join([part for part in [Adresse1, Adresse1Suite] if part]),
            Adresse2,
            Adresse3,
            ' '.join([part for part in [CodePostal, Commune, Cedex] if part]),
        ] if line]
        return '<br>'.join(lines)

    def filter_geom(self, src, val):
        lat, lng = val
        if lng == '' or lat == '':
            raise RowImportError(u"Required value for fields 'GmapLatitude' and 'GmapLongitude'.")
        geom = Point(float(lng), float(lat), srid=4326)  # WGS84
        geom.transform(settings.SRID)
        return geom

class Normandie61MainParser(NormandieMainParser):
    fields = {
        'eid': 'SyndicObjectID',
        'name': 'SyndicObjectName',
        'description_teaser': 'DescriptifSynthetique',
        'description': 'DescriptionCommerciale',
        'contact': ('Adresse1', 'Adresse1Suite', 'Adresse2', 'Adresse3', 'CP', 'Commune', 'Cedex'),
        'email': 'CommMail',
        'website': 'CommWeb',
        'geom': ('GmapLatitude', 'GmapLongitude'),
    }
class Normandie72MainParser(NormandieMainParser):
    base_url = 'http://cdt72.media.tourinsoft.eu/upload/'

    fields = {
        'eid': 'SyndicObjectID',
        'name': 'SyndicObjectName',
        'description_teaser': 'DescriptifSynthetique',
        'description': 'Descriptif',
        'contact': ('Adresse1', 'Adresse1Suite', 'Adresse2', 'Adresse3', 'CodePostal', 'Commune', 'Cedex'),
        'email': 'CommMail',
        'website': 'CommWeb',
        'geom': ('GmapLatitude', 'GmapLongitude'),
    }

    @property
    def items(self):
        return self.root['value']

    def next_row(self):
        skip = 0
        while True:
            params = {
                '$format': 'json',
                '$inlinecount': 'allpages',
                '$top': 1000,
                '$skip': skip,
            }
            response = requests.get(self.url, params=params)
            if response.status_code != 200:
                raise GlobalImportError(_(u"Failed to download {url}. HTTP status code {status_code}").format(url=self.url, status_code=response.status_code))
            self.root = response.json()
            self.nb = int(self.root['odata.count'])
            for row in self.items:
                yield {self.normalize_field_name(src): val for src, val in row.iteritems()}
            skip += 1000
            if skip >= self.nb:
                return

    def filter_attachments(self, src, val):
        if not val:
            return []
        return [subval.split('||') for subval in val.split('##') if subval.split('||')[0]]


class NormandieRestaurants61Parser(Normandie61MainParser):
    label = u"NormandieRestaurants61Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/cdb50f21-e7f3-40a3-a281-d6e1da557dc5/Objects'
    constant_fields = {
        'category': u"Restaurants",
        'published': True,
    }

class NormandieRestaurants72Parser(Normandie72MainParser):
    label = u"NormandieRestaurants72Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/3.0/cdt72/e01e961b-3f9f-4ab6-b17d-74fb115724b5/Objects'
    constant_fields = {
        'category': u"Restaurants",
        'published': True,
    }

class NormandieAccomodationRent61Parser(Normandie61MainParser):
    label = u"NormandieAccomodationRent61Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/0fbaa960-11ed-4a3c-aa33-adaee056150f/Objects'
    constant_fields = {
        'category': u"Hébergement",
        'published': True,
    }

class NormandieAccomodationHostel61Parser(Normandie61MainParser):
    label = u"NormandieAccomodationHostel61Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/7f5fda6f-340c-4617-9a94-a772642a9866/Objects'
    constant_fields = {
        'category': u"Hébergement",
        'published': True,
    }

class NormandieAccomodationCamping61Parser(Normandie61MainParser):
    label = u"NormandieAccomodationCamping61Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/5f0dbfb8-bb57-4c96-b334-c404e6b1b7f5/Objects'
    constant_fields = {
        'category': u"Hébergement",
        'published': True,
    }

class NormandieAccomodationVillage61Parser(Normandie61MainParser):
    label = u"NormandieAccomodationVillage61Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/e2c2d4a4-6e38-4b3a-9047-97dbfc5fa5ff/Objects'
    constant_fields = {
        'category': u"Hébergement",
        'published': True,
    }

class NormandieAccomodation72Parser(Normandie72MainParser):
    label = u"NormandieAccomodation72Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/3.0/cdt72/ddc71685-8c9d-4a1f-911d-8f2373a22a40/Objects'
    constant_fields = {
        'category': u"Hébergement",
        'published': True,
    }

class NormandieLeisureActivities61Parser(Normandie61MainParser):
    label = u"NormandieLeisureActivities61Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/b169bd47-3cc3-4b2a-ba7f-92b448107e0c/Objects'
    constant_fields = {
        'category': u"Loisirs - Découvertes",
        'published': True,
    }

class NormandieLeisureTasting61Parser(Normandie61MainParser):
    label = u"NormandieLeisureTasting61Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/3a8424cd-bd5a-44a5-8aed-02138918339d/Objects'
    constant_fields = {
        'category': u"Loisirs - Découvertes",
        'published': True,
    }

class NormandieLeisureLeisure61Parser(Normandie61MainParser):
    label = u"NormandieLeisureLeisure61Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/653708cf-cf68-4465-a58d-0b0cc50992ac/Objects'
    constant_fields = {
        'category': u"Loisirs - Découvertes",
        'published': True,
    }

class NormandieLeisureCulture61Parser(Normandie61MainParser):
    label = u"NormandieLeisureCulture61Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/a8ef6ec7-00ea-400e-8a02-25608805292f/Objects'
    constant_fields = {
        'category': u"Loisirs - Découvertes",
        'published': True,
    }

class NormandieLeisureNature61Parser(Normandie61MainParser):
    label = u"NormandieLeisureNature61Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/cdt61/4ae4f639-a516-4161-8215-4c63b8b696b0/Objects'
    constant_fields = {
        'category': u"Loisirs - Découvertes",
        'published': True,
    }

class NormandieLeisureCulture72Parser(Normandie72MainParser):
    label = u"NormandieLeisureCulture72Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/3.0/cdt72/49498dd2-030a-499f-97a6-3d0568781098/Objects'
    constant_fields = {
        'category': u"Loisirs - Découvertes",
        'published': True,
    }

class NormandieLeisureDiscovery72Parser(Normandie72MainParser):
    label = u"NormandieLeisureDiscovery72Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/3.0/cdt72/4ecafb85-8cd0-41a8-a385-92e6b37194db/Objects'
    constant_fields = {
        'category': u"Loisirs - Découvertes",
        'published': True,
    }


class NormandieLeisureLeisure72Parser(Normandie72MainParser):
    label = u"NormandieLeisureLeisure72Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/3.0/cdt72/2d720496-f215-43d9-b7ea-7955cf083b8b/Objects'

    constant_fields = {
        'category': u"Loisirs - Découvertes",
    }

    def parse_obj(self, row, operation):
        if not self.obj.pk:
            self.obj.published = True
        super(NormandieLeisureLeisure72Parser, self).parse_obj(row, operation)


class NormandieLeisureParty72Parser(Normandie72MainParser):
    model = TouristicEvent
    label = u"NormandieLeisureParty72Parser"
    url = 'http://wcf.tourinsoft.com/Syndication/3.0/cdt72/26a817a4-8c0a-4406-bd73-58d93f2dda4e/Objects'
    constant_fields = {
    }

