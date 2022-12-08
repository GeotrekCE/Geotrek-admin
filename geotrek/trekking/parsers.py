from datetime import date, timedelta
import json
from collections import defaultdict
import re
from tempfile import NamedTemporaryFile

from django.conf import settings
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import Point, GEOSGeometry, MultiLineString
from django.utils.translation import gettext as _, get_language

from geotrek.common.models import Label, Theme
from geotrek.common.parsers import (
    ShapeParser, AttachmentParserMixin, GeotrekParser, RowImportError, Parser, ApidaeBaseParser
)
from geotrek.common.utils.translation import get_translated_fields
from geotrek.trekking.models import OrderedTrekChild, POI, Service, Trek, DifficultyLevel, TrekNetwork, Accessibility


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


class ApidaeTranslatedField:

    apidae_prefix = 'libelle'

    def __init__(self, separator=''):
        self._separator = separator
        self._translated_items = defaultdict(list)

    def append(self, translated_value, transform_func=None):
        for lang in settings.MODELTRANSLATION_LANGUAGES:
            translation_value = translated_value.get(f'{ApidaeTranslatedField.apidae_prefix}{lang.capitalize()}', '')
            if transform_func:
                translation_value = transform_func(translation_value)
            self._translated_items[lang].append(translation_value)

    def to_dict(self):
        rv = {}
        for key, value in self._translated_items.items():
            rv[key] = self._separator.join(value)
        return rv


class ApidaeTrekParser(AttachmentParserMixin, ApidaeBaseParser):
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
        'accessibility_covering': 'informationsEquipement.itineraire.naturesTerrain.*',
        'gear': (
            'informationsEquipement.itineraire.referencesCartographiques',
            'informationsEquipement.itineraire.referencesTopoguides',
        ),
    }
    m2m_fields = {
        'source': 'gestion.membreProprietaire',
        'themes': 'presentation.typologiesPromoSitra.*',
        'labels': ['presentation.typologiesPromoSitra.*', 'localisation.environnements.*'],
        'related_treks': 'liens.liensObjetsTouristiquesTypes',
        'networks': 'informationsEquipement.activites',
        'accessibilities': 'informationsEquipement.itineraire.naturesTerrain.*',
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
        'accessibilities': 'name',
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
        },
        'accessibilities': {'create': True}
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
    natures_de_terrain_ids_as_accessibilities = [
        4244,  # Adapté aux poussettes de ville
        4245,  # Adapté aux poussettes tout terrain
    ]
    typologies_sitra_ids_as_labels = [
        1599,  # Déconseillé par mauvais temps
        1676,  # En plein air
        4639,  # Conseillé par forte chaleur
        4819,  # Paysages
        5022,  # Respirando
        4971,  # Inscrit au PDIPR
        3845,  # Itinéraire France vélo
        6566,  # Label Espace Cyclosport
        6049,  # Label Vélo et Fromages
        1582,  # Label VTT - FFC
        5538,  # Label VTT - FFCT
        6825,  # Station de Trail®
        6608,  # Site sur-fréquenté
        1602,  # Circuits de France
    ]
    typologies_sitra_ids_as_themes = [
        6155,  # Adrénaline
        6156,  # Au fil de l'eau
        6368,  # Familial
        6153,  # Faune
        6154,  # Flore
        6157,  # Géologie
        6163,  # Gourmande
        6158,  # Historique
        6679,  # Itinéraire d'accès à un refuge
        6159,  # Vue exceptionnelle
        6160,  # Pastoralisme
        6161,  # Volcanisme
    ]
    environnements_ids_as_labels = [
        135,  # A la campagne
        4630,  # Dans une réserve naturelle
        171,  # En montagne
        189,  # En moyenne montagne
        186,  # En haute montagne
        6238,  # Présence de troupeaux et chiens de protection
        3743,  # Au bord de l'eau
        147,  # Lac ou plan d'eau à moins de 300 m
        149,  # Rivière ou fleuve à moins de 300 m
        156,  # Etang à moins de 300 m
        153,  # En forêt
        187,  # Isolé
        195,  # Village à -2 km
        6464,  # Vue cascade
        4006,  # Vue sur fleuve ou rivière
        169,  # Vue montagne
        3978,  # Vue sur le vignoble
        6087,  # Vue panoramique
    ]
    activites_ids_as_networks = [
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
    types_clientele_ids_as_difficulty_levels = [
        587,  # Niveau vert - Très facile
        588,  # Niveau bleu - Modéré
        589,  # Niveau rouge - Difficile
        590,  # Niveau noir - Très difficile
        6669,  # Niveau orange - assez difficile
    ]

    guidebook_description_id = 6527
    default_trek_marking_description = {
        'libelleFr': 'Cet itinéraire est balisé.',
        'libelleEn': 'This trek is marked.',
    }
    trek_no_marking_description = {
        'libelleFr': 'Cet itinéraire n\'est pas balisé',
        'libelleEn': 'This trek is not marked',
    }
    apidae_translation_prefix = 'libelle'

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
                self.fields[f'{translated_field}_{lang}'] = f'{src}.{self.apidae_translation_prefix}{lang.capitalize()}'

    def apply_filter(self, dst, src, val):
        val = super().apply_filter(dst, src, val)
        # Can be called after a filter_*** to dispatch translated values into translation fields.
        if dst in self.translated_fields:
            if isinstance(val, dict) or isinstance(val, ApidaeTranslatedField):

                if isinstance(val, ApidaeTranslatedField):
                    val = val.to_dict()

                for key, final_value in val.items():
                    if key in settings.MODELTRANSLATION_LANGUAGES:
                        self.set_value(f'{dst}_{key}', src, final_value)

                val = val.get(get_language())
        return val

    def end(self):
        self._finalize_related_treks_association()

    def filter_eid(self, src, val):
        return str(val)

    def filter_geom(self, src, val):
        plan = self._find_gpx_plan_in_multimedia_items(val)
        gpx = self._fetch_gpx_from_url(plan)

        return ApidaeTrekParser._get_geom_from_gpx(gpx)

    def filter_labels(self, src, val):
        typologies, environnements = val
        translation_src = self._get_default_translation_src()
        filtered_val = []
        if typologies:
            filtered_val += [t[translation_src] for t in typologies if t['id'] in self.typologies_sitra_ids_as_labels]
        if environnements:
            filtered_val += [e[translation_src] for e in environnements if e['id'] in self.environnements_ids_as_labels]
        return self.apply_filter(
            dst='labels',
            src=src,
            val=filtered_val
        )

    def filter_themes(self, src, val):
        translation_src = self._get_default_translation_src()
        return self.apply_filter(
            dst='themes',
            src=src,
            val=[item[translation_src] for item in val if item['id'] in self.typologies_sitra_ids_as_themes]
        )

    def filter_description(self, src, val):
        ouverture, descriptifs, itineraire, tarifs = val
        return self.apply_filter(
            dst='description',
            src=src,
            val=self.__class__._make_description(ouverture, descriptifs, itineraire, tarifs)
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
            if tc['id'] in self.types_clientele_ids_as_difficulty_levels:
                difficulty_level = tc
                break
        if difficulty_level:
            translation_src = self._get_default_translation_src()
            return self.apply_filter(
                dst='difficulty',
                src=src,
                val=difficulty_level[translation_src]
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
        default_translation_fieldname = self._get_default_translation_src()
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
        translation_src = self._get_default_translation_src()
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

    def filter_accessibilities(self, src, val):
        translation_fieldname = self._get_default_translation_src()
        return self.apply_filter(
            dst='accessibilities',
            src=src,
            val=[
                item[translation_fieldname] for item in val
                if item['id'] in ApidaeTrekParser.natures_de_terrain_ids_as_accessibilities
            ]
        )

    def filter_accessibility_covering(self, src, val):
        natures_terrain = val
        natures_terrain_ids_as_coverings = [
            4240,  # Cailloux
            4243,  # Gravillons
            4242,  # Revêtement dur (goudron, ciment, plancher)
            4239,  # Rocher
            4241,  # Terre
        ]
        filtered_nt = [nt for nt in natures_terrain if nt['id'] in natures_terrain_ids_as_coverings]

        tf = ApidaeTranslatedField(separator=', ')
        for nt in filtered_nt:
            tf.append(translated_value=nt)
        self.apply_filter(
            dst='accessibility_covering',
            src=src,
            val=tf
        )

    def filter_gear(self, src, val):
        ref_carto, ref_topo = val
        if not ref_carto and not ref_topo:
            return None
        tf = ApidaeTranslatedField()
        if ref_carto:
            tf.append(translated_value=ref_carto, transform_func=ApidaeTrekParser._transform_description_to_html)
        if ref_topo:
            tf.append(translated_value=ref_topo, transform_func=ApidaeTrekParser._transform_description_to_html)
        return self.apply_filter(
            dst='gear',
            src=src,
            val=tf
        )

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
        return response.content

    @classmethod
    def _transform_description_to_html(cls, text):
        """Transform a descriptive text into HTML paragraphs."""
        html_blocks = []
        lines = text.replace('\r', '').split('\n')
        for line in lines:
            if not line:
                continue
            html_blocks.append(f'<p>{line}</p>')
        return ''.join(html_blocks)

    @classmethod
    def _transform_guidebook_to_html(cls, text):
        # This method can be overridden in var/conf/parsers.py.
        # FIXME: is there a better way to provide specific behaviors for parsing?
        return cls._transform_description_to_html(text)

    @classmethod
    def _make_marking_description(cls, itineraire):
        is_marked = itineraire['itineraireBalise'] == 'BALISE'
        if is_marked:
            marking_description = cls.default_trek_marking_description.copy()
            if itineraire.get('precisionsBalisage'):
                marking_description.update(itineraire['precisionsBalisage'])
        else:
            marking_description = cls.trek_no_marking_description.copy()
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
        with NamedTemporaryFile(mode='w+b', dir=settings.TMP_DIR) as ntf:
            ntf.write(data)
            ntf.flush()
            ds = DataSource(ntf.name)
            for layer_name in ('tracks', 'routes'):
                layer = ApidaeTrekParser._get_layer(ds, layer_name)
                geos = ApidaeTrekParser._maybe_get_linestring_from_layer(layer)
                if geos:
                    break
            geos.transform(settings.SRID)
            return geos

    @staticmethod
    def _get_layer(datasource, layer_name):
        for layer in datasource:
            if layer.name == layer_name:
                return layer

    @staticmethod
    def _convert_to_geos(geom):
        # FIXME: is it right to try to correct input geometries?
        # FIXME: how to log that info/spread errors?
        if geom.geom_type == 'MultiLineString' and any([ls for ls in geom if ls.num_points == 1]):
            # Handles that framework conversion fails when there are LineStrings of length 1
            geos_mls = MultiLineString([ls.geos for ls in geom if ls.num_points > 1])
            geos_mls.srid = geom.srid
            return geos_mls

        return geom.geos

    @staticmethod
    def _maybe_get_linestring_from_layer(layer):
        if layer.num_feat == 0:
            return None
        first_feature = layer[0]
        geos = ApidaeTrekParser._convert_to_geos(first_feature.geom)
        if geos.geom_type == 'MultiLineString':
            geos = geos.merged
        return geos

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
        result = re.match(r'(\d{4})-(\d{2})-(\d{2})', max_datetime_str)
        year, month, day = map(int, result.groups())
        max_date = date(year, month, day)
        # Note this exludes the limit date.
        return max_date > a_date

    @classmethod
    def _make_description(cls, ouverture=None, descriptifs=None, itineraire=None, tarifs=None):

        def get_guidebook():
            if not descriptifs:
                return None
            for d in descriptifs:
                if d['theme']['id'] == cls.guidebook_description_id:
                    return d
            return None

        def est_fermé_temporairement(ouverture):
            return ouverture.get('fermeTemporairement') == 'FERME_TEMPORAIREMENT'

        tf = ApidaeTranslatedField()

        if ouverture and est_fermé_temporairement(ouverture):
            tf.append(translated_value=ouverture['periodeEnClair'],
                      transform_func=cls._transform_description_to_html)

        guidebook = get_guidebook()
        if guidebook:
            tf.append(translated_value=guidebook['description'],
                      transform_func=cls._transform_guidebook_to_html)

        if ouverture and not est_fermé_temporairement(ouverture):
            tf.append(translated_value=ouverture['periodeEnClair'],
                      transform_func=cls._transform_description_to_html)

        if itineraire:
            tf.append(translated_value=cls._make_marking_description(itineraire),
                      transform_func=cls._transform_description_to_html)

        if tarifs and tarifs['indicationTarif'] == 'PAYANT':
            tf.append(translated_value=tarifs['tarifsEnClair'],
                      transform_func=cls._transform_description_to_html)

        return tf

    @staticmethod
    def _make_duration(duration_in_minutes=None, duration_in_days=None):
        """Returns the duration in hours. The method expects one argument or the other, not both. If both arguments have
         non-zero values the method only considers `duration_in_minutes` and discards `duration_in_days`."""
        if duration_in_minutes:
            return duration_in_minutes / 60
        elif duration_in_days:
            return duration_in_days * 24
        else:
            return None

    @classmethod
    def _get_default_translation_src(cls):
        return cls.apidae_translation_prefix + settings.MODELTRANSLATION_DEFAULT_LANGUAGE.capitalize()


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
    element_reference_ids = ApidaeTrekParser.typologies_sitra_ids_as_themes
    name_field = 'label'


class ApidaeTrekLabelParser(ApidaeReferenceElementParser):
    model = Label
    element_reference_ids = ApidaeTrekParser.typologies_sitra_ids_as_labels + ApidaeTrekParser.environnements_ids_as_labels
    name_field = 'name'


class ApidaeTrekDifficultyParser(ApidaeReferenceElementParser):
    model = DifficultyLevel
    element_reference_ids = ApidaeTrekParser.types_clientele_ids_as_difficulty_levels
    name_field = 'difficulty'


class ApidaeTrekNetworkParser(ApidaeReferenceElementParser):
    model = TrekNetwork
    element_reference_ids = ApidaeTrekParser.activites_ids_as_networks
    name_field = 'network'


class ApidaeTrekAccessibilityParser(ApidaeReferenceElementParser):
    model = Accessibility
    element_reference_ids = ApidaeTrekParser.natures_de_terrain_ids_as_accessibilities
    name_field = 'name'
