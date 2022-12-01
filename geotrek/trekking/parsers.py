from datetime import date, timedelta
import json
from collections import defaultdict
import re
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point, GEOSGeometry
from django.utils.translation import gettext as _, get_language

from geotrek.common.models import Label, Theme
from geotrek.common.parsers import (
    ShapeParser, AttachmentParserMixin, GeotrekParser, RowImportError, Parser, ApidaeParser
)
from geotrek.common.utils.translation import get_translated_fields
from geotrek.trekking.models import OrderedTrekChild, POI, Service, Trek, DifficultyLevel, TrekNetwork


class DurationParserMixin:
    def filter_duration(self, src, val):
        val = val.upper().replace(',', '.')
        try:
            if "H" in val:
                hours, minutes = val.split("H", 2)
                hours = float(hours.strip())
                minutes = float(minutes.strip()) if minutes.strip() else 0
                if hours < 0 or minutes < 0 or minutes >= 60:
                    raise ValueError
                return hours + minutes / 60
            else:
                hours = float(val.strip())
                if hours < 0:
                    raise ValueError
                return hours
        except (TypeError, ValueError):
            self.add_warning(_("Bad value '{val}' for field {src}. Should be like '2h30', '2,5' or '2.5'".format(val=val, src=src)))
            return None


class TrekParser(DurationParserMixin, AttachmentParserMixin, ShapeParser):
    label = "Import trek"
    label_fr = "Import itinéraires"
    label_en = "Import trek"
    model = Trek
    simplify_tolerance = 2
    eid = 'name'
    constant_fields = {
        'published': True,
        'deleted': False,
    }
    natural_keys = {
        'difficulty': 'difficulty',
        'route': 'route',
        'themes': 'label',
        'practice': 'name',
        'accessibilities': 'name',
        'networks': 'network'
    }

    def filter_geom(self, src, val):
        if val is None:
            return None
        if val.geom_type == 'MultiLineString':
            points = val[0]
            for i, path in enumerate(val[1:]):
                distance = Point(points[-1]).distance(Point(path[0]))
                if distance > 5:
                    self.add_warning(_("Not contiguous segment {i} ({distance} m) for geometry for field '{src}'").format(i=i + 2, p1=points[-1], p2=path[0], distance=int(distance), src=src))
                points += path
            return points
        elif val.geom_type != 'LineString':
            self.add_warning(_("Invalid geometry type for field '{src}'. Should be LineString, not {geom_type}").format(src=src, geom_type=val.geom_type))
            return None
        return val


class GeotrekTrekParser(GeotrekParser):
    """Geotrek parser for Trek"""

    url = None
    model = Trek
    constant_fields = {
        'published': True,
        'deleted': False,
    }
    replace_fields = {
        "eid": "uuid",
        "eid2": "second_external_id",
        "geom": "geometry"
    }
    url_categories = {
        "difficulty": "trek_difficulty",
        "route": "trek_route",
        "themes": "theme",
        "practice": "trek_practice",
        "accessibilities": "trek_accessibility",
        "networks": "trek_network",
        'labels': 'label',
        'source': 'source'
    }
    categories_keys_api_v2 = {
        'difficulty': 'label',
        'route': 'route',
        'themes': 'label',
        'practice': 'name',
        'accessibilities': 'name',
        'networks': 'label',
        'labels': 'name',
        'source': 'name'
    }
    natural_keys = {
        'difficulty': 'difficulty',
        'route': 'route',
        'themes': 'label',
        'practice': 'name',
        'accessibilities': 'name',
        'networks': 'network',
        'labels': 'name',
        'source': 'name'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/trek"

    def filter_parking_location(self, src, val):
        if val:
            return Point(val[0], val[1], srid=settings.API_SRID)

    def filter_points_reference(self, src, val):
        if val:
            geom = GEOSGeometry(json.dumps(val))
            return geom.transform(settings.SRID, clone=True)

    def end(self):
        """Add children after all treks imported are created in database."""
        super().end()
        self.next_url = f"{self.url}/api/v2/tour"
        try:
            params = {
                'in_bbox': ','.join([str(coord) for coord in self.bbox.extent]),
                'fields': 'steps,uuid'
            }
            response = self.request_or_retry(f"{self.next_url}", params=params)
            results = response.json()['results']
            final_children = {}
            for result in results:
                final_children[result['uuid']] = [step['uuid'] for step in result['steps']]

            for key, value in final_children.items():
                if value:
                    trek_parent_instance = Trek.objects.filter(eid=key)
                    if not trek_parent_instance:
                        self.add_warning(_(f"Trying to retrieve children for missing trek : could not find trek with UUID {key}"))
                        return
                    order = 0
                    for child in value:
                        try:
                            trek_child_instance = Trek.objects.get(eid=child)
                        except Trek.DoesNotExist:
                            self.add_warning(_(f"One trek has not be generated for {trek_parent_instance[0].name} : could not find trek with UUID {child}"))
                            continue
                        OrderedTrekChild.objects.get_or_create(parent=trek_parent_instance[0],
                                                               child=trek_child_instance,
                                                               order=order)
                        order += 1
        except Exception as e:
            self.add_warning(_(f"An error occured in children generation : {getattr(e, 'message', repr(e))}"))


class GeotrekServiceParser(GeotrekParser):
    """Geotrek parser for Service"""

    url = None
    model = Service
    constant_fields = {
        'deleted': False,
    }
    replace_fields = {
        "eid": "uuid",
        "geom": "geometry"
    }
    url_categories = {
        "type": "service_type",
    }
    categories_keys_api_v2 = {
        'type': 'name',
    }
    natural_keys = {
        'type': 'name'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/service"


class GeotrekPOIParser(GeotrekParser):
    """Geotrek parser for GeotrekPOI"""

    url = None
    model = POI
    constant_fields = {
        'published': True,
        'deleted': False,
    }
    replace_fields = {
        "eid": "uuid",
        "geom": "geometry"
    }
    url_categories = {
        "type": "poi_type",
    }
    categories_keys_api_v2 = {
        'type': 'label',
    }
    natural_keys = {
        'type': 'label',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/poi"


TYPOLOGIES_SITRA_IDS_AS_LABELS = [1599, 1676, 4639, 4819, 5022, 4971, 3845, 6566, 6049, 1582, 5538, 6825, 6608, 1602]
TYPOLOGIES_SITRA_IDS_AS_THEMES = [6155, 6156, 6368, 6153, 6154, 6157, 6163, 6158, 6679, 6159, 6160, 6161]
ENVIRONNEMENTS_IDS_AS_LABELS = [135, 4630, 171, 189, 186, 6238, 3743, 147, 149, 156, 153, 187, 195, 6464, 4006, 169, 3978, 6087]
APIDAE_ACTIVITIES_IDS_AS_NETWORKS = [
    3333,  # Itinéraire de randonnée pédestre
    3331,  # Parcours / sentier thématique
    5324,  # Parcours de marche nordique
    3283,  # Itinéraire cyclotourisme
    5447,  # Itinéraire de Vélo à Assistance Electrique
    3280,  # Véloroute et voie verte
    3284,  # Itinéraire VTT
    3281,  # Piste de descente VTT
    5446,  # Itinéraire enduro
    4174,  # Itinéraire Fat Bike
    6168,  # Itinéraire fauteuil tout terrain
    6224,  # Itinéraire gravel bike
    3313,  # Itinéraire de randonnée équestre
    4201,  # Itinéraire de Trail
    6225,  # Itinéraire de VTT à Assistance Électrique
]
TYPES_CLIENTELE_IDS_AS_DIFFICULTY_LEVELS = [
    587,  # Niveau vert - Très facile
    588,  # Niveau bleu - Modéré
    589,  # Niveau rouge - Difficile
    590,  # Niveau noir - Très difficile
    6669,  # Niveau orange - assez difficile
]
GUIDEBOOK_DESCRIPTION_ID = 6527
DEFAULT_TREK_MARKING_DESCRIPTION = {
    'libelleFr': 'Cet itinéraire est balisé.',
    'libelleEn': 'This trek is marked.',
}
TREK_NO_MARKING_DESCRIPTION = {
    'libelleFr': 'Cet itinéraire n\'est pas balisé',
    'libelleEn': 'This trek is not marked',
}


class ApidaeTrekParser(AttachmentParserMixin, ApidaeParser):
    model = Trek
    eid = 'eid'
    separator = None

    # Parameters to build the request
    url = 'https://api.apidae-tourisme.com/api/v002/recherche/list-objets-touristiques/'
    api_key = None
    project_id = None
    selection_id = None
    size = 20
    skip = 0
    responseFields = [
        'id',
        'nom',
        'multimedias',
        'gestion',
        'presentation',
        'localisation',
        'liens',
        'prestations',
        'ouverture',
        'descriptionTarif',
        'informationsEquipement',
    ]
    locales = ['fr', 'en']

    # Fields mapping
    fill_empty_translated_fields = True
    fields = {
        'name': 'nom',
        'description_teaser': 'presentation.descriptifCourt',
        'ambiance': 'presentation.descriptifDetaille',
        'description': (
            'ouverture',
            'presentation.descriptifsThematises.*',
            'informationsEquipement.itineraire',
            'descriptionTarif',
        ),
        'geom': 'multimedias',
        'eid': 'id',
        'advised_parking': 'localisation.adresse.adresse1',
        'departure': 'localisation.adresse.commune.nom',
        'access': 'localisation.geolocalisation.complement',
        'difficulty': 'prestations.typesClientele',
        'practice': 'informationsEquipement.activites',
        'duration': (
            'informationsEquipement.itineraire.dureeJournaliere',
            'informationsEquipement.itineraire.dureeItinerance',
        ),
        'advice': 'informationsEquipement.itineraire.passagesDelicats',
        'route': 'informationsEquipement.itineraire.itineraireType',
    }
    m2m_fields = {
        'source': 'gestion.membreProprietaire',
        'themes': 'presentation.typologiesPromoSitra.*',
        'labels': ['presentation.typologiesPromoSitra.*', 'localisation.environnements.*'],
        'related_treks': 'liens.liensObjetsTouristiquesTypes',
        'networks': 'informationsEquipement.activites',
    }
    natural_keys = {
        'source': 'name',
        'themes': 'label',
        'labels': 'name',
        'difficulty': 'difficulty',
        'related_treks': 'eid',
        'practice': 'name',
        'networks': 'network',
        'route': 'route',
    }
    field_options = {
        'source': {'create': True},
        'themes': {'create': True},
        'labels': {'create': True},
        'name': {'expand_translations': True},
        'description_teaser': {'expand_translations': True},
        'ambiance': {'expand_translations': True},
        'access': {'expand_translations': True},
        'difficulty': {'create': True},
        'related_treks': {'create': True},
        'practice': {'create': True},
        'networks': {'create': True},
        'advice': {'expand_translations': True},
        'route': {
            # Relevant default mapping considering routes in trekking data fixture.
            "mapping": {
                'BOUCLE': 'Boucle',
                'ALLER_RETOUR': 'Aller-retour',
                'ALLER_ITINERANCE': 'Traversée',
            }
        }
    }
    non_fields = {
        'attachments': 'illustrations'
    }

    # Relevant default mapping considering practices in trekking data fixture.
    # The practice key must be the name in the default language on your instance.
    practices_mapped_with_activities_ids = {
        'Pédestre': [
            3333,  # Itinéraire de randonnée pédestre
            3331,  # Parcours / sentier thématique
            5324,  # Parcours de marche nordique
        ],
        'Vélo': [
            3283,  # Itinéraire cyclotourisme
            5447,  # Itinéraire de Vélo à Assistance Electrique
            3280,  # Véloroute et voie verte
        ],
        'VTT': [
            3284,  # Itinéraire VTT
            3281,  # Piste de descente VTT
            5446,  # Itinéraire enduro
            4174,  # Itinéraire Fat Bike
            6168,  # Itinéraire fauteuil tout terrain
            6224,  # Itinéraire gravel bike
        ],
        'Cheval': [
            3313,  # Itinéraire de randonnée équestre
        ],
        'Trail': [
            4201,  # Itinéraire de Trail
        ],
        'VTTAE': [
            6225,  # Itinéraire de VTT à Assistance Électrique
        ],
    }
    practices_mapped_with_default_activities_ids = {
        'Pédestre': 3184,  # Sports pédestres
        'Vélo': 3113,  # Sports cyclistes
        'Cheval': 3165,  # Sports équestres
    }

    def __init__(self, *args, **kwargs):
        self._translated_fields = [field for field in get_translated_fields(self.model)]
        self._expand_fields_mapping_with_translation_fields()
        self._related_treks_mapping = defaultdict(list)
        super().__init__(*args, **kwargs)

    def _expand_fields_mapping_with_translation_fields(self):
        self.fields = self.fields.copy()
        translated_fields_to_expand = [
            field for field, options in self.field_options.items()
            if options.get('expand_translations') is True
        ]
        for translated_field in translated_fields_to_expand:
            src = self.fields[translated_field]
            del self.fields[translated_field]
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                self.fields[f'{translated_field}_{lang}'] = f'{src}.libelle{lang.capitalize()}'

    def apply_filter(self, dst, src, val):
        val = super().apply_filter(dst, src, val)
        # Can be called after a filter_*** to dispatch translated values into translation fields.
        if dst in self.translated_fields:
            if isinstance(val, dict):
                for key, final_value in val.items():
                    if key in settings.MODELTRANSLATION_LANGUAGES:
                        self.set_value(f'{dst}_{key}', src, final_value)
                val = val.get(get_language())
        return val

    def end(self):
        self._finalize_related_treks_association()

    def filter_geom(self, src, val):
        plan = self._find_gpx_plan_in_multimedia_items(val)
        gpx = self._fetch_gpx_from_url(plan)

        return ApidaeTrekParser._get_geom_from_gpx(gpx)

    def filter_labels(self, src, val):
        # TODO: unwrap val into typologies and environnements for clarity
        filtered_val = []
        for subval in val:
            if not subval:
                continue
            for item in subval:
                item_type = item['elementReferenceType']
                if ((item_type == 'TypologiePromoSitra' and item['id'] in TYPOLOGIES_SITRA_IDS_AS_LABELS)
                        or (item_type == 'Environnement' and item['id'] in ENVIRONNEMENTS_IDS_AS_LABELS)):
                    filtered_val.append(item['libelleFr'])
        return self.apply_filter(
            dst='labels',
            src=src,
            val=filtered_val
        )

    def filter_themes(self, src, val):
        return self.apply_filter(
            dst='themes',
            src=src,
            val=[item['libelleFr'] for item in val if item['id'] in TYPOLOGIES_SITRA_IDS_AS_THEMES]
        )

    def filter_description(self, src, val):
        ouverture, descriptifs, itineraire, tarifs = val
        return self.apply_filter(
            dst='description',
            src=src,
            val=ApidaeTrekParser._make_description(ouverture, descriptifs, itineraire, tarifs)
        )

    def filter_source(self, src, val):
        manager = val
        sources = self.apply_filter(
            dst='source',
            src=src,
            val=[manager['nom']]
        )
        source = sources[0]
        source.website = manager['siteWeb']
        source.save()
        return sources

    def filter_difficulty(self, src, val):
        types_clientele = val
        for tc in types_clientele:
            if tc['id'] in TYPES_CLIENTELE_IDS_AS_DIFFICULTY_LEVELS:
                difficulty_level = tc
                break
        else:
            return None
        return self.apply_filter(
            dst='difficulty',
            src=src,
            val=difficulty_level[f'libelle{settings.MODELTRANSLATION_DEFAULT_LANGUAGE.capitalize()}']
        )

    def filter_related_treks(self, src, val):
        liens = val
        child_treks = []
        for lien in liens:
            if lien['type'] == 'PARCOURS_ETAPE':
                child_trek = lien['objetTouristique']
                self._related_treks_mapping[self.obj.id].append(child_trek['id'])
                child_treks.append(lien['objetTouristique'])
        return self.apply_filter(
            dst='related_treks',
            src=src,
            val=[ct['id'] for ct in child_treks]
        )

    def filter_practice(self, src, val):
        activities = val
        activities_ids = [act['id'] for act in activities]
        return self.apply_filter(
            dst='practice',
            src=src,
            val=ApidaeTrekParser._get_practice_name_from_activities(activities_ids)
        )

    def filter_networks(self, src, val):
        activities = val
        default_translation_fieldname = f'libelle{settings.MODELTRANSLATION_DEFAULT_LANGUAGE.capitalize()}'
        filtered_activities = []
        for activity in activities:
            if default_translation_fieldname in activity:
                filtered_activities.append(activity[default_translation_fieldname])
        return self.apply_filter(
            dst='networks',
            src=src,
            val=filtered_activities
        )

    def filter_attachments(self, src, val):
        translation_src = f'libelle{settings.MODELTRANSLATION_DEFAULT_LANGUAGE.capitalize()}'
        illustrations = val
        rv = []
        for illustration in illustrations:
            files_metadata_list = illustration['traductionFichiers']
            if not ApidaeTrekParser._is_still_publishable_tomorrow(illustration) or not files_metadata_list:
                continue
            first_file_metadata = files_metadata_list[0]
            rv.append(
                (
                    first_file_metadata['url'],
                    illustration['legende'][translation_src],
                    illustration['copyright'][translation_src],
                    illustration['nom'][translation_src],
                )
            )
        return rv

    def filter_duration(self, src, val):
        duree_journaliere, duree_itinerance = val
        return ApidaeTrekParser._make_duration(duration_in_minutes=duree_journaliere, duration_in_days=duree_itinerance)

    def _finalize_related_treks_association(self):
        for parent_id, children_eids in self._related_treks_mapping.items():
            parent_trek = Trek.objects.get(pk=parent_id)
            order = 0
            for child_eid in children_eids:
                child_trek = Trek.objects.get(eid=child_eid)
                otc, _ = OrderedTrekChild.objects.get_or_create(
                    parent=parent_trek,
                    child=child_trek
                )
                otc.order = order
                otc.save()
                order += 1

    def _fetch_gpx_from_url(self, plan):
        ref_fichier_plan = plan['traductionFichiers'][0]
        if ref_fichier_plan['extension'] != 'gpx':
            raise RowImportError("Le plan de l'itinéraire APIDAE n'est pas au format GPX")
        response = self.request_or_retry(url=ref_fichier_plan['url'])
        # print('downloaded url {}, content size {}'.format(plan['traductionFichiers'][0]['url'], len(response.text)))
        return response.content

    @staticmethod
    def _transform_description_to_html(text):
        """Transform a descriptive text into HTML paragraphs."""
        html_blocks = []
        lines = text.replace('\r', '').split('\n')
        for line in lines:
            if not line:
                continue
            html_blocks.append(f'<p>{line}</p>')
        return ''.join(html_blocks)

    @staticmethod
    def _transform_guidebook_to_html(text):
        # This method can be overriden
        return ApidaeTrekParser._transform_description_to_html(text)

    @staticmethod
    def _make_marking_description(itineraire):
        is_marked = itineraire['itineraireBalise'] == 'BALISE'
        if is_marked:
            marking_description = DEFAULT_TREK_MARKING_DESCRIPTION.copy()
            if itineraire.get('precisionsBalisage'):
                marking_description.update(itineraire['precisionsBalisage'])
        else:
            marking_description = TREK_NO_MARKING_DESCRIPTION.copy()
        return marking_description

    @staticmethod
    def _find_gpx_plan_in_multimedia_items(items):
        plans = list(filter(lambda item: item['type'] == 'PLAN', items))
        if len(plans) > 1:
            raise RowImportError("APIDAE Trek has more than one map defined")
        return plans[0]

    @staticmethod
    def _get_geom_from_gpx(data):
        """Given GPX data as bytes it returns a geom."""
        # FIXME: is there another way than the temporary file? It seems not. `DataSource` really expects a filename.
        with NamedTemporaryFile(mode='w+b', dir='/opt/geotrek-admin/var/tmp') as ntf:
            ntf.write(data)
            ntf.flush()
            ds = DataSource(ntf.name)
            for layer_name in ('tracks', 'routes'):
                layer = ApidaeTrekParser._get_layer(ds, layer_name)
                if not layer:
                    continue
                geom = ApidaeTrekParser._maybe_get_linestring_from_layer(layer)
                if geom:
                    break
            geos = geom.geos
            geos.transform(settings.SRID)
            return geos

    @staticmethod
    def _get_layer(datasource, layer_name):
        for layer in datasource:
            if layer.name == layer_name:
                return layer
        return None

    @staticmethod
    def _maybe_get_linestring_from_layer(layer):
        if layer.num_feat == 0:
            return None
        first_entity = layer[0]
        if first_entity.geom.geom_type == 'MultiLineString':
            geom = first_entity.geom[0]
        else:
            geom = first_entity.geom
        return geom

    @staticmethod
    def _find_matching_practice_in_mapping(activities_ids, mapping):
        returned_practice_name = None
        for activity_id in activities_ids:
            for practice_name, value in mapping.items():
                try:
                    for mapped_activity_id in value:
                        if activity_id == mapped_activity_id:
                            returned_practice_name = practice_name
                except TypeError:
                    mapped_activity_id = value
                    if activity_id == mapped_activity_id:
                        returned_practice_name = practice_name
        return returned_practice_name

    @staticmethod
    def _get_practice_name_from_activities(activities_ids):
        for mapping in (
            ApidaeTrekParser.practices_mapped_with_activities_ids,
            ApidaeTrekParser.practices_mapped_with_default_activities_ids
        ):
            practice_name = ApidaeTrekParser._find_matching_practice_in_mapping(activities_ids, mapping)
            if practice_name:
                break
        return practice_name

    @staticmethod
    def _is_still_publishable_tomorrow(illustration):
        # The illustration is still publishable tomorrow if tomorrow is strictly before the limit date.
        # This is to ensure the next import will always occur before the time part of the limit date.
        return ApidaeTrekParser._is_still_publishable_on(illustration, date.today() + timedelta(days=1))

    @staticmethod
    def _is_still_publishable_on(illustration, a_date):
        max_datetime_str = illustration.get('dateLimiteDePublication')
        if not max_datetime_str:
            return True
        # Regexp parsing because Python does not handle timezone with no colon,
        # and because we don't know when the import is run we drop the time part.
        max_date_str = re.match(r'(\d{4}-\d{2}-\d{2})', max_datetime_str).group(0)
        max_date = date.fromisoformat(max_date_str)
        # Note this exludes the limit date.
        return max_date > a_date

    @staticmethod
    def _make_description(ouverture=None, descriptifs=None, itineraire=None, tarifs=None):
        html_description = defaultdict(lambda: '')

        def append_to_html_description(translated_field,
                                       transform_func=ApidaeTrekParser._transform_description_to_html):
            for lang in settings.MODELTRANSLATION_LANGUAGES:
                try:
                    html_description[lang] += transform_func(translated_field[f'libelle{lang.capitalize()}'])
                except KeyError:
                    pass

        def get_guidebook():
            if not descriptifs:
                return None
            for d in descriptifs:
                if d['theme']['id'] == GUIDEBOOK_DESCRIPTION_ID:
                    return d
            return None

        def est_fermé_temporairement(ouverture):
            return ouverture.get('fermeTemporairement') == 'FERME_TEMPORAIREMENT'

        if ouverture and est_fermé_temporairement(ouverture):
            append_to_html_description(ouverture['periodeEnClair'])

        guidebook = get_guidebook()
        if guidebook:
            append_to_html_description(guidebook['description'],
                                       transform_func=ApidaeTrekParser._transform_guidebook_to_html)

        if ouverture and not est_fermé_temporairement(ouverture):
            append_to_html_description(ouverture['periodeEnClair'])

        if itineraire:
            append_to_html_description(ApidaeTrekParser._make_marking_description(itineraire))

        if tarifs and tarifs['indicationTarif'] == 'PAYANT':
            append_to_html_description(tarifs['tarifsEnClair'])

        return html_description

    @staticmethod
    def _make_duration(duration_in_minutes=None, duration_in_days=None):
        """Returns the duration in hours. Expects only one of the argument to have a non-zero value."""
        assert not (duration_in_minutes and duration_in_days)
        if duration_in_minutes:
            return duration_in_minutes / 60
        elif duration_in_days:
            return duration_in_days * 24
        else:
            return None


class ApidaeReferenceElementParser(Parser):

    url = 'https://api.apidae-tourisme.com/api/v002/referentiel/elements-reference/'

    api_key = None
    project_id = None
    element_reference_ids = None
    name_field = None
    # Fields mapping is generated in __init__

    def __init__(self, *args, **kwargs):
        self._add_multi_languages_fields_mapping()
        self._set_eid_fieldname()
        super().__init__(*args, **kwargs)

    def _add_multi_languages_fields_mapping(self):
        self.fields = {
            f'{self.name_field}_{lang}': f'libelle{lang.capitalize()}'
            for lang in settings.MODELTRANSLATION_LANGUAGES
        }

    def _set_eid_fieldname(self):
        self.eid = f'{self.name_field}_{settings.MODELTRANSLATION_DEFAULT_LANGUAGE}'

    @property
    def items(self):
        return self.root

    def next_row(self):
        params = {
            'apiKey': self.api_key,
            'projetId': self.project_id,
            'elementReferenceIds': self.element_reference_ids,
        }
        response = self.request_or_retry(self.url, params={'query': json.dumps(params)})
        self.root = response.json()
        self.nb = len(self.root)
        for row in self.items:
            yield row

    def normalize_field_name(self, name):
        return name


class ApidaeTrekThemeParser(ApidaeReferenceElementParser):
    model = Theme
    element_reference_ids = TYPOLOGIES_SITRA_IDS_AS_THEMES
    name_field = 'label'


class ApidaeTrekLabelParser(ApidaeReferenceElementParser):
    model = Label
    element_reference_ids = TYPOLOGIES_SITRA_IDS_AS_LABELS + ENVIRONNEMENTS_IDS_AS_LABELS
    name_field = 'name'


class ApidaeTrekDifficultyParser(ApidaeReferenceElementParser):
    model = DifficultyLevel
    element_reference_ids = TYPES_CLIENTELE_IDS_AS_DIFFICULTY_LEVELS
    name_field = 'difficulty'


class ApidaeTrekNetworkParser(ApidaeReferenceElementParser):
    model = TrekNetwork
    element_reference_ids = APIDAE_ACTIVITIES_IDS_AS_NETWORKS
    name_field = 'network'

# TODO
# class ApidaeTrekAccessibilityParser(ApidaeReferenceElementParser):
#     model = Accessibility
#     element_reference_ids = None
