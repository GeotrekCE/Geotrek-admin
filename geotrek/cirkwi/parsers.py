from django.conf import settings
from django.contrib.gis.geos import Point
from django.utils.translation import gettext as _

from geotrek.common.parsers import AttachmentParserMixin, XmlParser
from geotrek.tourism.models import TouristicContent, TouristicContentType1
from geotrek.trekking.models import Trek
from geotrek.trekking.parsers import ApidaeTrekParser


class CirkwiParser(AttachmentParserMixin, XmlParser):
    eid = 'eid'
    default_language = settings.MODELTRANSLATION_DEFAULT_LANGUAGE
    field_options = {
        "geom": {"required": True},
        "name": {"required": True},
    }
    constant_fields = {
        'published': True,
    }

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

    def filter_description(self, src, val):
        descr, compl_title, compl_descr = val
        if compl_title and compl_descr:
            return f"{descr}\n\n\n{compl_title}: {compl_descr}"
        return descr

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
        "description": ("informations/information[@langue='<LANG>']/description",
                        "informations/information[@langue='<LANG>']/informations_complementaires/information_complementaire/titre",
                        "informations/information[@langue='<LANG>']/informations_complementaires/information_complementaire/description"),
        "geom": "sens_circuit/fichier_trace@@url",
    }
    constant_fields = {
        'practice': "Pédestre"
    }
    non_fields = {
        'attachments': "informations/information[@langue='<LANG>']/medias/images/image/*"
    }
    natural_keys = {
        'practice': 'name'
    }

    def filter_geom(self, src, val):
        response = self.request_or_retry(url=val)
        return ApidaeTrekParser._get_geom_from_gpx(response.content)


class CirkwiTouristicContentParser(CirkwiParser):
    model = TouristicContent
    default_language = settings.MODELTRANSLATION_DEFAULT_LANGUAGE
    results_path = 'poi'
    fields = {
        "eid": "@@id_poi",
        "name": "informations/information[@langue='<LANG>']/titre",
        "description": ("informations/information[@langue='<LANG>']/description",
                        "informations/information[@langue='<LANG>']/informations_complementaires/information_complementaire/titre",
                        "informations/information[@langue='<LANG>']/informations_complementaires/information_complementaire/description"),
        "geom": ("adresse/position/lng", "adresse/position/lat"),
        "practical_info": ("adresse/num", "adresse/rue", "adresse/cp", "adresse/ville", "informations/information[@langue='<LANG>']/informations_complementaires/information_complementaire/*"),
        "category": "categories/categorie/*",
    }
    m2m_fields = {
        "type1": "categories/categorie/*",
    }
    non_fields = {
        'attachments': "informations/information[@langue='<LANG>']/medias/images/image/*"
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
            infos += '<strong>Adresse : </strong><br>'
        if num and street:
            infos += f"{num} {street}<br>"
        if code and city:
            infos += f"{code} {city}<br>"
        for other_info in other_infos:
            infos += f"<br><strong>{other_info.find('titre').text} : </strong><br>"
            infos += f"{other_info.find('description').text}<br>"
        return infos

    def filter_category(self, src, val):
        name = val[0].attrib["nom"]
        return self.apply_filter('category', src, name)

    def filter_type1(self, src, val):
        if val is None or len(val) < 2:
            return None
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
