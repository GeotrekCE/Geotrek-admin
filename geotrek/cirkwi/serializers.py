import datetime

from django.contrib.gis.db.models.functions import Transform
from django.urls import reverse
from django.utils import translation
from django.utils.timezone import utc, make_aware
from django.utils.translation import get_language
from django.utils.xmlutils import SimplerXMLGenerator

from mapentity.serializers import plain_text


from geotrek.cirkwi.models import CirkwiTag


def timestamp(dt):
    epoch = make_aware(datetime.datetime(1970, 1, 1), utc)
    return str(int((dt - epoch).total_seconds()))


class CirkwiPOISerializer:
    def __init__(self, request, stream, get_params=None):
        self.xml = SimplerXMLGenerator(stream, 'utf8')
        self.request = request
        self.stream = stream

    def serialize_field(self, name, value, attrs={}):
        if not value and not attrs:
            return
        value = str(value)
        self.xml.startElement(name, attrs)
        if '<' in value or u'>' in value or '&' in value:
            self.stream.write('<![CDATA[%s]]>' % value)
        else:
            self.xml.characters(value)
        self.xml.endElement(name)

    def serialize_medias(self, request, pictures):
        if not pictures:
            return
        self.xml.startElement('medias', {})
        self.xml.startElement('images', {})
        for picture in pictures[:10]:
            self.xml.startElement('image', {})
            if picture['legend']:
                self.serialize_field('legende', picture['legend'])
            self.serialize_field('url', request.build_absolute_uri(picture['url']))
            if picture['author']:
                self.serialize_field('credit', picture['author'])
            self.xml.endElement('image')
        self.xml.endElement('images')
        self.xml.endElement('medias')

    def serialize_pois(self, pois):
        if not pois:
            return
        for poi in pois:
            self.xml.startElement('poi', {
                'date_creation': timestamp(poi.date_insert),
                'date_modification': timestamp(poi.date_update),
                'id_poi': str(poi.pk),
            })
            if poi.type.cirkwi:
                self.xml.startElement('categories', {})
                self.serialize_field('categorie', str(poi.type.cirkwi.eid), {'nom': poi.type.cirkwi.name})
                self.xml.endElement('categories')
            orig_lang = translation.get_language()
            self.xml.startElement('informations', {})
            for lang in poi.published_langs:
                translation.activate(lang)
                self.xml.startElement('information', {'langue': lang})
                self.serialize_field('titre', poi.name)
                self.serialize_field('description', plain_text(poi.description))
                self.serialize_medias(self.request, poi.serializable_pictures)
                self.xml.endElement('information')
            translation.activate(orig_lang)
            self.xml.endElement('informations')
            self.xml.startElement('adresse', {})
            self.xml.startElement('position', {})
            coords = poi.geom.transform(4326, clone=True).coords
            self.serialize_field('lat', round(coords[1], 7))
            self.serialize_field('lng', round(coords[0], 7))
            self.xml.endElement('position')
            self.xml.endElement('adresse')
            self.xml.endElement('poi')

    def serialize(self, pois):
        self.xml.startDocument()
        self.xml.startElement('pois', {'version': '2'})
        self.serialize_pois(pois)
        self.xml.endElement('pois')
        self.xml.endDocument()


class CirkwiTrekSerializer(CirkwiPOISerializer):
    ADDITIONNAL_INFO = ('departure', 'arrival', 'ambiance', 'access', 'accessibility_infrastructure',
                        'advised_parking', 'public_transport', 'advice')

    def __init__(self, request, stream, get_params=None):
        super().__init__(request, stream, get_params)
        self.request = request
        self.exclude_pois = get_params.get('withoutpois', None)

    def serialize_additionnal_info(self, trek, name):
        value = getattr(trek, name)
        if not value:
            return
        value = plain_text(value)
        self.xml.startElement('information_complementaire', {})
        self.serialize_field('titre', trek._meta.get_field(name).verbose_name)
        self.serialize_field('description', value)
        self.xml.endElement('information_complementaire')

    def serialize_tracking_info(self, trek):
        attrs = {}
        self.xml.startElement('portals', {})
        for portal in trek.portal.all():
            attrs['id'] = str(portal.pk)
            attrs['nom'] = portal.name
            self.serialize_field('portal', '', attrs)
        self.xml.endElement('portals')
        self.xml.startElement('sources', {})
        for source in trek.source.all():
            attrs['id'] = str(source.pk)
            attrs['nom'] = source.name
            self.serialize_field('source', '', attrs)
        self.xml.endElement('sources')
        if trek.structure:
            attrs['id'] = str(trek.structure.pk)
            attrs['nom'] = trek.structure.name
            self.serialize_field('structure', '', attrs)

    def serialize_locomotions(self, trek):
        attrs = {}
        if trek.practice and trek.practice.cirkwi:
            attrs['type'] = trek.practice.cirkwi.name
            attrs['id_locomotion'] = str(trek.practice.cirkwi.eid)
        if trek.difficulty and trek.difficulty.cirkwi_level:
            attrs['difficulte'] = str(trek.difficulty.cirkwi_level)
        if trek.duration:
            attrs['duree'] = str(int(trek.duration * 3600))
        if attrs:
            self.xml.startElement('locomotions', {})
            self.serialize_field('locomotion', '', attrs)
            self.xml.endElement('locomotions')

    def serialize_description(self, trek):
        description = trek.description_teaser
        if description and trek.description:
            description += '\n\n'
            description += trek.description
        if description:
            self.serialize_field('description', plain_text(description))

    def serialize_tags(self, trek):
        tag_ids = list(trek.themes.filter(cirkwi_id__isnull=False).values_list('cirkwi_id', flat=True))
        tag_ids += trek.accessibilities.filter(cirkwi_id__isnull=False).values_list('cirkwi_id', flat=True)
        if trek.difficulty and trek.difficulty.cirkwi_id:
            tag_ids.append(trek.difficulty.cirkwi_id)
        if tag_ids:
            self.xml.startElement('tags_publics', {})
            for tag in CirkwiTag.objects.filter(id__in=tag_ids):
                self.serialize_field('tag_public', '', {'id': str(tag.eid), 'nom': tag.name})
            self.xml.endElement('tags_publics')

    def serialize_labels(self, trek):
        for label in trek.labels.all():
            value = plain_text(label.advice)
            self.xml.startElement('information_complementaire', {})
            self.serialize_field('titre', label.name)
            self.serialize_field('description', value)
            self.xml.endElement('information_complementaire')

    # TODO: parking location (POI?), points_reference
    def serialize(self, treks):
        self.xml.startDocument()
        self.xml.startElement('circuits', {'version': '2'})
        for trek in treks:
            self.xml.startElement('circuit', {
                'date_creation': timestamp(trek.date_insert),
                'date_modification': timestamp(trek.date_update),
                'id_circuit': str(trek.pk),
            })
            orig_lang = translation.get_language()
            self.xml.startElement('informations', {})
            for lang in trek.published_langs:
                translation.activate(lang)
                self.xml.startElement('information', {'langue': lang})
                self.serialize_field('titre', trek.name)
                self.serialize_description(trek)
                self.serialize_medias(self.request, trek.serializable_pictures)
                if any([getattr(trek, name) for name in self.ADDITIONNAL_INFO]):
                    self.xml.startElement('informations_complementaires', {})
                    for name in self.ADDITIONNAL_INFO:
                        self.serialize_additionnal_info(trek, name)
                    self.serialize_labels(trek)
                    self.xml.endElement('informations_complementaires')
                self.serialize_tags(trek)
                self.xml.endElement('information')
            translation.activate(orig_lang)
            self.xml.endElement('informations')
            self.serialize_field('distance', int(trek.length))
            self.serialize_locomotions(trek)
            kml_url = reverse('trekking:trek_kml_detail',
                              kwargs={'lang': get_language(), 'pk': trek.pk, 'slug': trek.slug})
            self.serialize_field('fichier_trace', '', {'url': self.request.build_absolute_uri(kml_url)})
            self.xml.startElement('tracking_information', {})
            self.serialize_tracking_info(trek)
            self.xml.endElement('tracking_information')
            if not self.exclude_pois and trek.published_pois:
                self.xml.startElement('pois', {})
                self.serialize_pois(trek.published_pois.annotate(transformed_geom=Transform('geom', 4326)))
                self.xml.endElement('pois')
            self.xml.endElement('circuit')
        self.xml.endElement('circuits')
        self.xml.endDocument()
