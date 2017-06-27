import copy
import datetime
import json

import gpxpy.gpx
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils import translation
from django.utils.translation import get_language, ugettext_lazy as _
from django.utils.timezone import utc, make_aware
from django.utils.xmlutils import SimplerXMLGenerator
from rest_framework import serializers as rest_serializers

from mapentity.serializers import GPXSerializer, plain_text

from geotrek.common.serializers import (
    PictogramSerializerMixin, ThemeSerializer,
    TranslatedModelSerializer, PicturesSerializerMixin,
    PublishableSerializerMixin, RecordSourceSerializer,
    TargetPortalSerializer
)
from geotrek.authent import models as authent_models
from geotrek.cirkwi.models import CirkwiTag
from geotrek.zoning.serializers import ZoningSerializerMixin
from geotrek.altimetry.serializers import AltimetrySerializerMixin
from geotrek.trekking import models as trekking_models


class TrekGPXSerializer(GPXSerializer):
    def end_object(self, trek):
        super(TrekGPXSerializer, self).end_object(trek)
        for poi in trek.pois.all():
            geom_3d = poi.geom_3d.transform(4326, clone=True)  # GPX uses WGS84
            wpt = gpxpy.gpx.GPXWaypoint(latitude=geom_3d.y,
                                        longitude=geom_3d.x,
                                        elevation=geom_3d.z)
            wpt.name = u"%s: %s" % (poi.type, poi.name)
            wpt.description = poi.description
            self.gpx.waypoints.append(wpt)


class DifficultyLevelSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.ReadOnlyField(source='difficulty')

    class Meta:
        model = trekking_models.DifficultyLevel
        fields = ('id', 'pictogram', 'label')


class RouteSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.ReadOnlyField(source='route')

    class Meta:
        model = trekking_models.Route
        fields = ('id', 'pictogram', 'label')


class NetworkSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    name = rest_serializers.ReadOnlyField(source='network')

    class Meta:
        model = trekking_models.Route
        fields = ('id', 'pictogram', 'name')


class PracticeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.ReadOnlyField(source='name')

    class Meta:
        model = trekking_models.Practice
        fields = ('id', 'pictogram', 'label')


class AccessibilitySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    label = rest_serializers.ReadOnlyField(source='name')

    class Meta:
        model = trekking_models.Accessibility
        fields = ('id', 'pictogram', 'label')


class TypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.Practice
        fields = ('id', 'pictogram', 'name')


class WebLinkCategorySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.WebLinkCategory
        fields = ('id', 'pictogram', 'label')


class WebLinkSerializer(TranslatedModelSerializer):
    category = WebLinkCategorySerializer()

    class Meta:
        model = trekking_models.WebLink
        fields = ('id', 'name', 'category', 'url')


class CloseTrekSerializer(TranslatedModelSerializer):
    category_id = rest_serializers.ReadOnlyField(source='prefixed_category_id')

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'category_id')


class RelatedTrekSerializer(TranslatedModelSerializer):
    pk = rest_serializers.ReadOnlyField(source='id')
    category_slug = rest_serializers.SerializerMethodField()

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'pk', 'slug', 'name', 'category_slug')

    def get_category_slug(self, obj):
        if settings.SPLIT_TREKS_CATEGORIES_BY_PRACTICE and obj.practice:
            return obj.practice.slug
        else:
            # Translators: This is a slug (without space, accent or special char)
            return _('trek')


class TrekRelationshipSerializer(rest_serializers.ModelSerializer):
    published = rest_serializers.ReadOnlyField(source='trek_b.published')
    trek = RelatedTrekSerializer(source='trek_b')

    class Meta:
        model = trekking_models.TrekRelationship
        fields = ('has_common_departure', 'has_common_edge', 'is_circuit_step',
                  'trek', 'published')


class StructureSerializer(rest_serializers.ModelSerializer):
    class Meta:
        model = authent_models.Structure
        fields = ('id', 'name')


class ChildSerializer(TranslatedModelSerializer):
    class Meta:
        model = trekking_models.Trek
        fields = ('id', )


class TrekSerializer(PublishableSerializerMixin, PicturesSerializerMixin,
                     AltimetrySerializerMixin, ZoningSerializerMixin,
                     TranslatedModelSerializer):
    difficulty = DifficultyLevelSerializer()
    route = RouteSerializer()
    networks = NetworkSerializer(many=True)
    themes = ThemeSerializer(many=True)
    practice = PracticeSerializer()
    usages = PracticeSerializer(many=True)  # Rando v1 compat
    accessibilities = AccessibilitySerializer(many=True)
    web_links = WebLinkSerializer(many=True)
    relationships = TrekRelationshipSerializer(many=True, source='published_relationships')
    treks = CloseTrekSerializer(many=True, source='published_treks')
    source = RecordSourceSerializer(many=True)
    portal = TargetPortalSerializer(many=True)
    children = rest_serializers.ReadOnlyField(source='children_id')
    parents = rest_serializers.ReadOnlyField(source='parents_id')
    previous = rest_serializers.ReadOnlyField(source='previous_id')
    next = rest_serializers.ReadOnlyField(source='next_id')

    # Idea: use rest-framework-gis
    parking_location = rest_serializers.SerializerMethodField()
    points_reference = rest_serializers.SerializerMethodField()

    gpx = rest_serializers.SerializerMethodField('get_gpx_url')
    kml = rest_serializers.SerializerMethodField('get_kml_url')
    structure = StructureSerializer()

    # For consistency with touristic contents
    type1 = TypeSerializer(source='usages', many=True)
    type2 = TypeSerializer(source='accessibilities', many=True)
    category = rest_serializers.SerializerMethodField()

    # Method called to retrieve relevant pictures based on settings
    pictures = rest_serializers.SerializerMethodField()

    def __init__(self, instance=None, *args, **kwargs):
        # duplicate each trek for each one of its accessibilities
        if instance and hasattr(instance, '__iter__') and settings.SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY:
            treks = []
            for trek in instance:
                treks.append(trek)
                for accessibility in trek.accessibilities.all():
                    clone = copy.copy(trek)
                    clone.accessibility = accessibility
                    treks.append(clone)
            instance = treks

        super(TrekSerializer, self).__init__(instance, *args, **kwargs)

        from geotrek.tourism import serializers as tourism_serializers

        if settings.SPLIT_TREKS_CATEGORIES_BY_PRACTICE:
            del self.fields['type1']
        if settings.SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY:
            del self.fields['type2']

        self.fields['information_desks'] = tourism_serializers.InformationDeskSerializer(many=True)
        self.fields['touristic_contents'] = tourism_serializers.CloseTouristicContentSerializer(many=True, source='published_touristic_contents')
        self.fields['touristic_events'] = tourism_serializers.CloseTouristicEventSerializer(many=True, source='published_touristic_events')

    class Meta:
        model = trekking_models.Trek
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'geom'
        fields = ('id', 'departure', 'arrival', 'duration', 'duration_pretty',
                  'description', 'description_teaser', 'networks', 'advice',
                  'ambiance', 'difficulty', 'information_desks', 'themes',
                  'practice', 'accessibilities', 'usages', 'access', 'route',
                  'public_transport', 'advised_parking', 'web_links', 'is_park_centered',
                  'disabled_infrastructure', 'parking_location', 'relationships',
                  'points_reference', 'gpx', 'kml', 'source', 'portal', 'type1',
                  'type2', 'category', 'structure', 'treks', 'children', 'parents',
                  'previous', 'next') + \
            AltimetrySerializerMixin.Meta.fields + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields

    def get_pictures(self, obj):
        pictures_list = []
        pictures_list.extend(obj.serializable_pictures)
        if settings.TREK_WITH_POIS_PICTURES:
            for poi in obj.published_pois:
                pictures_list.extend(poi.serializable_pictures)
        return pictures_list

    def get_parking_location(self, obj):
        if not obj.parking_location:
            return None
        return obj.parking_location.transform(settings.API_SRID, clone=True).coords

    def get_points_reference(self, obj):
        if not obj.points_reference:
            return None
        geojson = obj.points_reference.transform(settings.API_SRID, clone=True).geojson
        return json.loads(geojson)

    def get_gpx_url(self, obj):
        return reverse('trekking:trek_gpx_detail', kwargs={'lang': get_language(), 'pk': obj.pk, 'slug': obj.slug})

    def get_kml_url(self, obj):
        return reverse('trekking:trek_kml_detail', kwargs={'lang': get_language(), 'pk': obj.pk, 'slug': obj.slug})

    def get_category(self, obj):
        accessibility = getattr(obj, 'accessibility', None)
        if accessibility:
            data = {
                'id': accessibility.prefixed_id,
                'label': accessibility.name,
                'pictogram': accessibility.get_pictogram_url(),
                'slug': accessibility.slug,
            }
        elif settings.SPLIT_TREKS_CATEGORIES_BY_PRACTICE and obj.practice:
            data = {
                'id': obj.prefixed_category_id,
                'label': obj.practice.name,
                'pictogram': obj.practice.get_pictogram_url(),
                'slug': obj.practice.slug,
            }
        else:
            data = {
                'id': obj.category_id_prefix,
                'label': obj._meta.verbose_name,
                'pictogram': '/static/trekking/trek.svg',
                # Translators: This is a slug (without space, accent or special char)
                'slug': _('trek'),
            }
        if settings.SPLIT_TREKS_CATEGORIES_BY_PRACTICE:
            data['order'] = obj.practice and obj.practice.order
        else:
            data['order'] = settings.TREK_CATEGORY_ORDER
        if not settings.SPLIT_TREKS_CATEGORIES_BY_PRACTICE:
            data['type1_label'] = obj._meta.get_field('practice').verbose_name
        if not settings.SPLIT_TREKS_CATEGORIES_BY_ACCESSIBILITY:
            data['type2_label'] = obj._meta.get_field('accessibilities').verbose_name
        return data


class POITypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.POIType
        fields = ('id', 'pictogram', 'label')


class ClosePOISerializer(TranslatedModelSerializer):
    type = POITypeSerializer()

    class Meta:
        model = trekking_models.Trek
        fields = ('id', 'slug', 'name', 'type')


class POISerializer(PublishableSerializerMixin, PicturesSerializerMixin,
                    ZoningSerializerMixin, TranslatedModelSerializer):
    type = POITypeSerializer()
    structure = StructureSerializer()

    def __init__(self, *args, **kwargs):
        super(POISerializer, self).__init__(*args, **kwargs)

        from geotrek.tourism import serializers as tourism_serializers

        self.fields['touristic_contents'] = tourism_serializers.CloseTouristicContentSerializer(many=True, source='published_touristic_contents')
        self.fields['touristic_events'] = tourism_serializers.CloseTouristicEventSerializer(many=True, source='published_touristic_events')

    class Meta:
        model = trekking_models.Trek
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'geom'
        fields = ('id', 'description', 'type',) + \
            ('min_elevation', 'max_elevation', 'structure') + \
            ZoningSerializerMixin.Meta.fields + \
            PublishableSerializerMixin.Meta.fields + \
            PicturesSerializerMixin.Meta.fields


class ServiceTypeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = trekking_models.ServiceType
        fields = ('id', 'pictogram', 'name')


class ServiceSerializer(rest_serializers.ModelSerializer):
    type = ServiceTypeSerializer()
    structure = StructureSerializer()

    class Meta:
        model = trekking_models.Service
        id_field = 'id'  # By default on this model it's topo_object = OneToOneField(parent_link=True)
        geo_field = 'geom'
        fields = ('id', 'type', 'structure')


def timestamp(dt):
    epoch = make_aware(datetime.datetime(1970, 1, 1), utc)
    return str(int((dt - epoch).total_seconds()))


class CirkwiPOISerializer(object):
    def __init__(self, request, stream):
        self.xml = SimplerXMLGenerator(stream, 'utf8')
        self.request = request
        self.stream = stream

    def serialize_field(self, name, value, attrs={}):
        if not value and not attrs:
            return
        value = unicode(value)
        self.xml.startElement(name, attrs)
        if u'<' in value or u'>' in value or u'&' in value:
            self.stream.write('<![CDATA[%s]]>' % value)
        else:
            self.xml.characters(value)
        self.xml.endElement(name)

    def serialize_medias(self, request, pictures):
        if not pictures:
            return
        self.xml.startElement('medias', {})
        self.xml.startElement('images', {})
        for picture in pictures:
            self.xml.startElement('image', {})
            self.serialize_field('legende', picture['legend'])
            self.serialize_field('url', request.build_absolute_uri(picture['url']))
            self.serialize_field('credit', picture['author'])
            self.xml.endElement('image')
        self.xml.endElement('images')
        self.xml.endElement('medias')

    def serialize_pois(self, pois):
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
            self.serialize_field('lat', coords[1])
            self.serialize_field('lng', coords[0])
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
    def __init__(self, request, stream, get_params=None):
        super(CirkwiTrekSerializer, self).__init__(request, stream)
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

    def serialize_trace(self, trek):
        self.xml.startElement('trace', {})
        coords = trek.geom.transform(4326, clone=True).coords
        if trek.geom.geom_typeid == 5:
            coords = coords[0]
        elif trek.geom.geom_typeid != 1:
            coords = []
        for c in coords:
            self.xml.startElement('point', {})
            self.serialize_field('lat', c[1])
            self.serialize_field('lng', c[0])
            self.xml.endElement('point')
        self.xml.endElement('trace')

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
            description += u'\n\n'
            description += trek.description
        if description:
            self.serialize_field('description', plain_text(description))

    def serialize_tags(self, trek):
        self.xml.startElement('tags_publics', {})
        tag_ids = list(trek.themes.values_list('cirkwi_id', flat=True))
        tag_ids += trek.accessibilities.values_list('cirkwi_id', flat=True)
        if trek.difficulty and trek.difficulty.cirkwi_id:
            tag_ids.append(trek.difficulty.cirkwi_id)
        for tag in CirkwiTag.objects.filter(id__in=tag_ids):
            self.serialize_field('tag_public', '', {'id': str(tag.eid), 'nom': tag.name})
        self.xml.endElement('tags_publics')

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
                self.xml.startElement('informations_complementaires', {})
                self.serialize_additionnal_info(trek, 'departure')
                self.serialize_additionnal_info(trek, 'arrival')
                self.serialize_additionnal_info(trek, 'ambiance')
                self.serialize_additionnal_info(trek, 'access')
                self.serialize_additionnal_info(trek, 'disabled_infrastructure')
                self.serialize_additionnal_info(trek, 'advised_parking')
                self.serialize_additionnal_info(trek, 'public_transport')
                self.serialize_additionnal_info(trek, 'advice')
                self.xml.endElement('informations_complementaires')
                self.serialize_tags(trek)
                self.xml.endElement('information')
            translation.activate(orig_lang)
            self.xml.endElement('informations')
            self.serialize_field('distance', int(trek.length))
            self.serialize_locomotions(trek)
            self.serialize_trace(trek)
            if not self.exclude_pois:
                if trek.published_pois:
                    self.xml.startElement('pois', {})
                    self.serialize_pois(trek.published_pois.transform(4326, field_name='geom'))
                    self.xml.endElement('pois')
            self.xml.endElement('circuit')
        self.xml.endElement('circuits')
        self.xml.endDocument()
