import os
import shutil
import tempfile
import urllib2
import xml.etree.ElementTree as ET

from django.contrib.gis.geos import Point

from geotrek.common.parsers import Parser, AttachmentParserMixin
from geotrek.trekking.models import Trek, WebLink, POI
from geotrek.trekking.parsers import TrekParser


class FtpShapeParserMixin(object):
    def parse(self, filename=None, limit=None):
        tmpdir = tempfile.mkdtemp(suffix='geotrek_import')
        try:
            for ext in ('dbf', 'prj', 'sbn', 'sbx', 'shp', 'shx'):
                url = '{url}.{ext}'.format(url=self.url, ext=ext)
                path = os.path.join(tmpdir, os.path.basename(url))
                response = urllib2.urlopen(url)
                with open(path, 'w') as f:
                    shutil.copyfileobj(response, f)
            url = '{url}.shp'.format(url=self.url)
            path = os.path.join(tmpdir, os.path.basename(url))
            ret = super(FtpShapeParserMixin, self).parse(path, limit)
        finally:
            shutil.rmtree(tmpdir)
        return ret


class XmlParserMixin(object):
    def next_row(self):
        response = urllib2.urlopen(self.url)
        self.root = ET.fromstring(response.read())
        self.nb = len(self.root)
        for row in self.root:
            yield {field.tag: field.text for field in row}

    def normalize_field_name(self, name):
        return name


class ItiShpParser(FtpShapeParserMixin, TrekParser):
    url = 'ftp://makina:ccgsig05600@212.44.230.63/itineraires_geom'
    eid = 'eid'
    delete = True
    fields = {
        'eid': 'REFERENCE',
        'geom': 'GEOM',
    }
    constant_fields = {
        'published_fr': True,
        'published_en': True,
        # 'published_it': True,
        'is_park_centered': False,
        'deleted': False,
    }


class ItiXmlParser(XmlParserMixin, TrekParser):
    url = 'ftp://makina:ccgsig05600@212.44.230.63/itineraires.xml'
    eid = 'eid'
    update_only = True
    fields = {
        'eid': 'REFERENCE',
        'name': 'NOM',
        'name_en': 'NOM_ITI_A',
        'departure': 'DEPART',
        'arrival': 'ARRIVEE',
        'route': 'TYPE_ITI',
        'practice': 'TYPE_PRATI',
        'description_teaser': 'DESCRIPT',
        'description_teaser_en': 'DESC_GEN_A',
        'access': 'ACCES',
        'access_en': 'DESC_ACC_A',
        'duration': 'DUREE',
        'public_transport': 'TRANSP_DESC',
        'public_transport_en': 'DESC_TC_A',
        'advice': 'RECOMMAND',
        'advice_en': 'RECOMM_A',
        'difficulty': 'DIFFICULTE',
        'advised_parking': 'PARKING',
        'description': ('DESCRIPTD', 'VARIANTE', 'TOPOGUIDE'),
        'description_en': ('DESC_DET_A', 'DESC_VAR_A', 'DESC_TPG_A'),
        'disabled_infrastructure': 'ACCESSIBILITE',
        'ambiance': 'PATRIMOINE',
    }
    m2m_fields = {
        'networks': ('CATEGORIE', 'BAL_COULEUR'),
        'web_links': 'IGN',
    }
    non_fields = {
        'length': 'DISTANCE',
        'ascent': 'DENIV_POSI',
        'descent': 'DENIV_NEGA',
        'min_elevation': 'ALT_MIN',
        'max_elevation': 'ALT_MAX',
    }
    natural_keys = {
        'difficulty': 'difficulty',
        'route': 'route',
        'themes': 'label',
        'practice': 'name',
        'accessibilities': 'name',
        'networks': 'network',
    }

    def filter_networks(self, src, val):
        val = ' - '.join([i for i in val if i])
        return self.apply_filter('networks', src, val)

    def filter_description(self, src, val):
        description = ('<p>', val[0], '</p>')
        if val[1]:
            description += ('<h3>Variante</h3><p>', val[1], '</p>')
        if val[2]:
            description += ('<h3>Topoguide</h3><p>', val[2], '</p>')
        return ''.join(description)

    def filter_description_en(self, src, val):
        if not val[0]:
            return None
        description = ('<p>', val[0], '</p>')
        if val[1]:
            description += ('<h3>Variant</h3><p>', val[1], '</p>')
        if val[2]:
            description += ('<h3>Topoguide</h3><p>', val[2], '</p>')
        return ''.join(description)

    def filter_web_links(self, src, val):
        if not val:
            return []
        url_ign = "http://loisirs.ign.fr/catalogsearch/result/?q={val}".format(val=val)
        weblink, created = WebLink.objects.get_or_create(url=url_ign, name=val)
        return [weblink]

    def save_int(self, dst, src, val):
        if self.parse_field(dst, src, val):
            self.obj.save(update_fields=[dst])
            return [dst]
        else:
            return []

    def save_length(self, src, val):
        if val[-2:].lower() == 'km':
            val = val[:-2].strip() + '000'
        elif val[-1:].lower() == 'm':
            val = val[:-1].strip()
        else:
            val = val.strip()
        return self.save_int('length', src, float(val))

    def save_ascent(self, src, val):
        return self.save_int('ascent', src, int(val))

    def save_descent(self, src, val):
        return self.save_int('descent', src, int(val))

    def save_min_elevation(self, src, val):
        return self.save_int('min_elevation', src, int(val))

    def save_max_elevation(self, src, val):
        return self.save_int('max_elevation', src, int(val))


class ItiDocParser(XmlParserMixin, AttachmentParserMixin, Parser):
    url = 'ftp://makina:ccgsig05600@212.44.230.63/itineraires_documents.xml'
    model = Trek
    eid = 'eid'
    update_only = True
    delete_attachments = True
    fields = {
        'eid': 'REFERENCE',
    }
    non_fields = {
        'attachments': ('NUMERO', 'AUTEUR', 'LEGENDE'),
    }

    def filter_attachments(self, src, val):
        (numero, author, name) = val
        url = os.path.join(os.path.dirname(self.url), 'ITI_docs', numero)
        return [(url, author, name)]


class POIXmlParser(XmlParserMixin, Parser):
    url = 'ftp://makina:ccgsig05600@212.44.230.63/points_interet.xml'
    model = POI
    eid = 'eid'
    delete = True
    fields = {
        'eid': 'REF',
        'geom': ('LONG', 'LAT'),
        'name_fr': 'NOM',
        'name_en': 'NOM_A',
        # 'name_it': 'NOM_I',
        'description_fr': 'COMMENTAIRE',
        'description_en': 'COMMENTAIRE_A',
        # 'description_it': 'COMMENTAIRE_I',
        'type': 'CATEGORIE',
    }
    constant_fields = {
        'published_fr': True,
        'published_en': True,
        # 'published_it': True,
    }
    natural_keys = {
        'type': 'label',
    }

    def filter_geom(self, src, val):
        (x, y) = val
        if not x or not y:
            return None
        return Point(float(x), float(y))


class POIDocParser(XmlParserMixin, AttachmentParserMixin, Parser):
    url = 'ftp://makina:ccgsig05600@212.44.230.63/points_interet_documents.xml'
    model = POI
    eid = 'eid'
    update_only = True
    delete_attachments = True
    fields = {
        'eid': 'REF',
    }
    non_fields = {
        'attachments': ('NUMI', 'AUT', 'LEG'),
    }

    def filter_attachments(self, src, val):
        (numero, author, name) = val
        url = os.path.join(os.path.dirname(self.url), 'POI_docs', numero)
        return [(url, author, name)]
