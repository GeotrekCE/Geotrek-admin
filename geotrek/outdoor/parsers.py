from geotrek.common.parsers import (ApidaeBaseParser, AttachmentParserMixin, GeotrekParser, GlobalImportError, Parser)
from geotrek.outdoor.models import Site


class GeotrekSiteParser(GeotrekParser):
    """Geotrek parser for Outoor Site"""
    fill_empty_translated_fields = True
    url = None
    model = Site
    replace_fields = {
        "eid": "uuid",
        "geom": "geometry"
    }
    url_categories = {
        "practice": "outdoor_practice",
        "ratings": "outdoor_rating",
        "themes": "theme",
        "type": "outdoor_sitetype",
        'labels': 'label',
        'source': 'source',
        'managers': 'organism',
        'structure': 'structure',
    }
    categories_keys_api_v2 = {
        "practice": "name",
        "ratings": "name",
        "themes": "label",
        "type": "name",
        'labels': 'name',
        'source': 'name',
        'managers': 'name',
        'structure': 'name',
    }
    natural_keys = {
        "practice": "name",
        "ratings": "name",
        "themes": "label",
        "type": "name",
        'labels': 'name',
        'source': 'name',
        'managers': 'organism',
        'structure': 'name',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/outdoor_site"
        print("AFTER INIT 9999999999999999999999999999999999999999999999999999999")

    def end(self):
        """Add children after all treks imported are created in database."""
        #super().end()
        print("MAKE LINK BETWEEN SITES")
