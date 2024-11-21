import requests
import xml.etree.ElementTree as ET

from django.conf import settings
from django.contrib.gis.geos import Point, MultiPoint, GEOSGeometry
from django.utils.translation import gettext as _

from geotrek.common.utils.parsers import get_geom_from_gpx
from geotrek.trekking.models import DifficultyLevel
from geotrek.cirkwi.models import CirkwiLocomotion
from geotrek.common.parsers import AttachmentParserMixin, GlobalImportError, Parser, RowImportError
from geotrek.tourism.models import TouristicContent, TouristicContentType1
from geotrek.trekking.models import Trek, Practice


class CirkwiParser(AttachmentParserMixin, Parser):
    """
    auth: Allows to configure HTTP auth on parser requests
    create: Create a Cirkwi Locomotion from label, before trying to map it to a Trek Practice with same label
    delete: Delete old objects that are now missing from flux (based on 'get_to_delete_kwargs')
    default_language: Allows to define which language this parser will populate by default
    eid: Field to use as Cirwki id
    provider: Allows to differentiate multiple Parser for the same model
    rows: Quantity of objects to load per page (Cirkwi pagination)
    update_only: Do not delete previous objects, and query Cirkwi API with most recent date_update
    """
    auth = ()
    create = False
    delete = False
    default_language = settings.MODELTRANSLATION_DEFAULT_LANGUAGE
    eid = 'eid'
    provider = "Cirkwi"
    rows = 10
    update_only = False

    field_options = {
        "geom": {"required": True},
        "name": {"required": True},
    }
    constant_fields = {
        'published': True,
    }
    non_fields = {
        'attachments': "informations/information[@langue='<LANG>']/medias/images/image/*"
    }

    def __init__(self, *args, **kwargs):
        # Extract URL parameter to use to retrieve updates only (will be used in 'next_row' method)
        self.updated_after = None
        if self.update_only and self.model.objects.filter(provider__exact=self.provider).exists():
            last_update_timestamp = self.model.objects.filter(provider__exact=self.provider).latest(
                'date_update').date_update.timestamp()
            self.updated_after = str(int(last_update_timestamp))
        super().__init__(*args, **kwargs)

    def normalize_field_name(self, name):
        return name

    def next_row(self):
        # Get data from local file :
        if self.filename:
            with open(self.filename) as f:
                xml_root = ET.fromstring(f.read())
            # Yield objects given XML path in 'results_path'
            entries = xml_root.findall(self.results_path)
            self.nb = len(entries)
            for row in entries:
                yield row

        # Get data from API URL :
        else:
            # Make first query to retrieve objects count
            # We don't need the objects yet, just need to access 'nb_objects', so set params to 0
            params = {
                'first': 0,
                'rows': 0,
            }
            if self.updated_after:
                params['end-time'] = self.updated_after
            response = requests.get(self.url, params=params, auth=self.auth)
            if response.status_code != 200:
                raise GlobalImportError(_(u"Failed to download {url}. HTTP status code {status_code}").format(
                    url=self.url, status_code=response.status_code))
            # Save objects count
            self.nb = int(ET.fromstring(response.content).find("listing_ids", {}).attrib['nb_objects'])

            # Make several requests, using Cirkwi pagination parameters, until all objects are downloaded
            first = 0
            while first <= self.nb:
                params['first'] = first
                params['rows'] = self.rows
                response = requests.get(self.url, params=params, auth=self.auth)
                if response.status_code != 200:
                    raise GlobalImportError(_(u"Failed to download {url}. HTTP status code {status_code}").format(
                        url=self.url, status_code=response.status_code))
                xml_root = ET.fromstring(response.content)
                # Yield objects given XML path in 'results_path'
                entries = xml_root.findall(self.results_path)
                for row in entries:
                    yield row
                first += self.rows

    def get_part(self, dst, src, val):
        # Recursively extract XML attributes
        if '@@' in src and src[:2] != '@@':
            part, attrib = src.split('@@', 1)
            return self.get_part(dst, f"@@{attrib}", val.find(part))
        # Extract XML attributes
        elif src.startswith('@@'):
            return val.attrib[src[2:]]
        else:
            # Replace language attribute
            if "'<LANG>'" in src:
                src = src.replace("<LANG>", self.default_language)
            # Return a list of XML elements
            if src.endswith('/*'):
                return val.findall(src[:-2])
            # Return inner text if XML element exists
            if val.find(src) is None:
                return None
            return val.find(src).text

    def filter_attachments(self, src, val):
        attachments = []
        for attachment in val:
            legend = attachment.find('legende')
            if legend is not None:
                legend = legend.text
            url = attachment.find('url').text
            author = attachment.find('credit')
            if author is not None:
                author = author.text
            attachments.append([url, legend, author])
        return attachments


class CirkwiTrekParser(CirkwiParser):
    model = Trek
    results_path = 'circuit'
    fields = {
        "eid": "@@id_circuit",
        "name": "informations/information[@langue='<LANG>']/titre",
        "description_teaser": "informations/information[@langue='<LANG>']/description",
        "description": ("informations/information[@langue='<LANG>']/informations_complementaires/information_complementaire/titre",
                        "informations/information[@langue='<LANG>']/informations_complementaires/information_complementaire/description",
                        "infos_parcours/info_parcours/informations/information[@langue='<LANG>']/description/*"),
        "points_reference": ("infos_parcours/info_parcours/adresse/position/lat/*",
                             "infos_parcours/info_parcours/adresse/position/lng/*"),
        "geom": "fichier_trace@@url",
        "practice": ("locomotions/locomotion@@type", "locomotions/locomotion@@id_locomotion"),
        "difficulty": "locomotions/locomotion@@difficulte",
        "duration": "locomotions/locomotion@@duree",
    }

    def filter_geom(self, src, val):
        response = self.request_or_retry(url=val)
        return get_geom_from_gpx(response.content)

    def filter_practice(self, src, val):
        """
        We try to :
        1 - Find matching Cirkwi Locomotion, OR create it if `create` is set to `True`
        2 - If 1 was successful, find Trek Practice matching this Cirkwi Locomotion by label. We do not create extra Practices automatically.
        """
        label, eid = val
        try:
            cirkwi_locomotion = CirkwiLocomotion.objects.get(name=label, eid=eid)
        except CirkwiLocomotion.DoesNotExist:
            if self.create:
                cirkwi_locomotion = CirkwiLocomotion.objects.create(name=label, eid=eid)
                self.add_warning(
                    _("{model} '{val}' did not exist in Geotrek-Admin and was automatically created").format(
                        model='Cirkwi Locomotion', val=label))
            else:
                self.add_warning(_("{model} '{val}' does not exists in Geotrek-Admin. Please add it").format(
                    model='Cirkwi Locomotion', val=val))
                raise RowImportError
        try:
            practice = Practice.objects.get(cirkwi=cirkwi_locomotion)
        except Practice.DoesNotExist:
            try:
                practice = Practice.objects.get(name=label, cirkwi__isnull=True)
                practice.cirkwi = cirkwi_locomotion
                practice.save()
            except Practice.DoesNotExist:
                self.add_warning(
                    _("No Practice matching Cirkwi Locomotion '{type}' (id: '{id}') was found. Please add it").format(
                        type=label,
                        id=eid
                    )
                )
                raise RowImportError
        return practice

    def filter_duration(self, src, val):
        if val != "0":
            return int(val) / 3600
        return None

    def filter_difficulty(self, src, val):
        """
        We try to find matching Difficulty Level through its Cirkwi id.
        We do not create extra Difficulty Levels automatically.
        """
        difficulty = None
        if val != '0':
            try:
                difficulty = DifficultyLevel.objects.get(cirkwi_level=int(val))
            except DifficultyLevel.DoesNotExist:
                self.add_warning(_("{model} '{val}' does not exists in Geotrek-Admin. Please add it").format(
                    model=_('Difficulty Level with Cirkwi Level'), val=val))
        return difficulty

    def filter_description(self, src, val):
        desc = ""
        compl_title, compl_descr, step_descriptions = val
        if compl_title and compl_descr:
            desc += f"{compl_title}: {compl_descr}"
        # Extract text from all XML Elements, and build ordered list for 'points_reference'
        step_descriptions = list(map(lambda x: x.text, step_descriptions))
        if step_descriptions:
            desc += "<ol>\r\n"
            for step_description in step_descriptions:
                desc += f"<li>{step_description}</li>"
            desc += "</ol>"
        return desc

    def filter_points_reference(self, src, val):
        step_lats, step_longs = val
        step_lats = list(map(lambda x: float(x.text), step_lats))
        step_longs = list(map(lambda x: float(x.text), step_longs))
        steps = MultiPoint([Point(x, y, srid=4326) for x, y in zip(step_longs, step_lats)])
        geom = GEOSGeometry(steps, srid=4326)
        return geom.transform(settings.SRID, clone=True)


class CirkwiTouristicContentParser(CirkwiParser):
    model = TouristicContent
    default_language = settings.MODELTRANSLATION_DEFAULT_LANGUAGE
    results_path = 'poi'
    fields = {
        "eid": "@@id_poi",
        "name": "informations/information[@langue='<LANG>']/titre",
        "description": "informations/information[@langue='<LANG>']/description",
        "geom": ("adresse/position/lng", "adresse/position/lat"),
        "practical_info": ("adresse/num", "adresse/rue", "adresse/cp", "adresse/ville", "informations/information[@langue='<LANG>']/informations_complementaires/information_complementaire/*"),
        "category": "categories/categorie/*",
    }
    m2m_fields = {
        "type1": "categories/categorie/*",
    }
    field_options = {
        "geom": {"required": True},
        "name": {"required": True},
        'category': {'create': True},
        'type1': {'create': True},
    }
    natural_keys = {
        'category': 'label',
        'type1': 'label',
    }

    def filter_practical_info(self, src, val):
        num, street, code, city, other_infos = val
        infos = ''
        if (num and street) or (code and city):
            address = _("Address")
            infos += f'<strong>{address} : </strong><br>'
        if num and street:
            infos += f"{num} {street}<br>"
        if code and city:
            infos += f"{code} {city}<br>"
        for other_info in other_infos:
            infos += f"<br><strong>{other_info.find('titre').text} : </strong><br>"
            infos += f"{other_info.find('description').text}<br>"
        return infos

    def filter_category(self, src, val):
        # val[0] is category
        # val[1] is type1
        name = val[0].attrib["nom"]
        return self.apply_filter('category', src, name)

    def filter_type1(self, src, val):
        """
        We try to find matching TouristicContentType1 through its label and category,
        OR create it if `create` is set to `True` for 'type1' in mapping 'field_options'
        """
        # val[0] is category
        # val[1] is type1
        if val is None or len(val) < 2:
            return []
        label = val[1].attrib["nom"]
        if self.field_options.get("type1", {}).get("create", False):
            type1, __ = TouristicContentType1.objects.get_or_create(category=self.obj.category, label=label)
        else:
            try:
                type1 = TouristicContentType1.objects.get(category=self.obj.category, label=label)
            except TouristicContentType1.DoesNotExist:
                self.add_warning(
                    _("Type 1 '{type}' does not exist for category '{cat}'. Please add it").format(
                        type=label, cat=self.obj.category.label))
                return []
        return [type1]

    def filter_geom(self, src, val):
        lng, lat = val
        geom = Point(float(lng), float(lat), srid=4326)  # WGS84
        geom.transform(settings.SRID)
        return geom
