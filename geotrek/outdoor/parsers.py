from django.conf import settings
from geotrek.common.parsers import (ApidaeBaseParser, AttachmentParserMixin, GeotrekParser, GlobalImportError, Parser)
from geotrek.outdoor.models import Practice, Rating, RatingScale, Sector, Site


class GeotrekSiteParser(GeotrekParser):
    """Geotrek parser for Outoor Site"""
    fill_empty_translated_fields = True
    url = None
    model = Site
    replace_fields = {
        "eid": "uuid",
        "geom": "geometry",
        "scale": "ratingscale"
    }
    url_categories = {
        "themes": "theme",
        "type": "outdoor_sitetype",
        'labels': 'label',
        'source': 'source',
        'managers': 'organism',
        'structure': 'structure',
    }
    categories_keys_api_v2 = {
        "practice": "name",
        "sector": "name",
        "rating": "name",
        "scale": "name",
        "ratingscale": "name",
        "themes": "label",
        "type": "name",
        'labels': 'name',
        'source': 'name',
        'managers': 'name',
        'structure': 'name',
    }
    natural_keys = {
        "practice": "name",
        "themes": "label",
        "type": "name",
        'labels': 'name',
        'source': 'name',
        'managers': 'organism',
        'structure': 'name',
    }
    parents = {}

    def get_id_from_mapping(self, mapping, value):
        for dest_id, source_id in mapping.items():
            if source_id == value:
                return dest_id
        return None

    def init_outdoor_category(self, category, model, join_field=None, extra_fields={}):
        # Get categories as JSON response
        response = self.request_or_retry(f"{self.url}/api/v2/outdoor_{category}")
        results = response.json().get('results', [])

        # Init mapping variable for this category if it does not exist
        if category not in self.field_options.keys():
            self.field_options[category] = {}
        if "mapping" not in self.field_options[category].keys():
            self.field_options[category]["mapping"] = {}

        # Iter over category JSON results
        for result in results:

            # Extract label in default language from JSON
            label = result["name"]
            if isinstance(label, dict):
                if label[settings.MODELTRANSLATION_DEFAULT_LANGUAGE]:
                    replaced_label = self.replace_mapping(label[settings.MODELTRANSLATION_DEFAULT_LANGUAGE], f'outdoor_{category}')
            else:
                if label:
                    replaced_label = self.replace_mapping(label, f'outdoor_{category}')

            # Extract other category attributes in default language from JSON
            fields = {}
            for field in extra_fields:
                if isinstance(result[field], dict):
                    if result[field][settings.MODELTRANSLATION_DEFAULT_LANGUAGE]:
                        fields[field] = result[field][settings.MODELTRANSLATION_DEFAULT_LANGUAGE]
                else:
                    fields[field] = result[field]

            # Extract field that will become a ForeignKey from JSON response, using mapping
            if join_field:
                mapping_key = self.replace_fields.get(join_field, join_field)
                mapped_value = self.get_id_from_mapping(self.field_options[mapping_key]["mapping"], result[join_field])
                if not mapped_value:
                    continue  # Ignore some results if related category was not retrieved
                fields[f"{join_field}_id"] = mapped_value

            # Create or update object given all the fields that we extracted above
            category_obj, _ = model.objects.update_or_create(**{'name': replaced_label}, defaults=fields)

            # Remember this object in mapping for next call
            self.field_options[category]["mapping"][category_obj.pk] = result['id']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_outdoor_category('sector', Sector)
        self.init_outdoor_category('practice', Practice, join_field='sector')
        self.init_outdoor_category('ratingscale', RatingScale, join_field='practice')
        self.init_outdoor_category('rating', Rating, join_field='scale', extra_fields=['description', 'order', 'color'])
        self.next_url = f"{self.url}/api/v2/outdoor_site"

    def filter_practice(self, src, val):
        if val:
            practice_id = self.get_id_from_mapping(self.field_options["practice"]["mapping"], val)
            if practice_id:
                return Practice.objects.get(pk=practice_id)
        return None

    def filter_ratings(self, src, val):
        ratings = []
        for subval in val:
            rating_id = self.get_id_from_mapping(self.field_options["rating"]["mapping"], subval)
            if rating_id:
                ratings.append(Rating.objects.get(pk=rating_id).pk)
        return ratings

    def parse_row(self, row):
        super().parse_row(row)
        self.parents[row['uuid']] = row['parent_uuid']

    def end(self):
        """Add children after all Sites imported are created in database."""
        for child, parent in self.parents.items():
            try:
                parent_site = Site.objects.get(eid=parent)
            except Site.DoesNotExist:
                self.add_warning(f"Trying to retrieve missing parent (UUID: {parent}) for child Site (UUID: {child})")
                continue
            try:
                child_site = Site.objects.get(eid=child)
            except Site.DoesNotExist:
                self.add_warning(f"Trying to retrieve missing child (UUID: {child}) for parent Site (UUID: {parent})")
                continue
            child_site.parent = parent_site
            child_site.save()
