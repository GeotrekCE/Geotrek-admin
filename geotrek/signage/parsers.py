from geotrek.common.parsers import GeotrekParser
from geotrek.signage.models import Signage


class GeotrekSignageParser(GeotrekParser):
    """Geotrek parser for Signage"""
    fill_empty_translated_fields = True
    url = None
    model = Signage
    constant_fields = {
        "deleted": False
    }
    replace_fields = {
        "eid": "uuid",
        "geom": "geometry"
    }
    url_categories = {
        "structure": "structure",
        'sealing': 'signage_sealing',
        'conditions': 'signage_condition',
        'type': 'signage_type',
    }
    categories_keys_api_v2 = {
        "structure": "name",
        'conditions': 'label',
        'sealing': 'label',
        'type': 'label'
    }
    natural_keys = {
        "structure": "name",
        'conditions': 'label',
        'sealing': 'label',
        'type': 'label'
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.next_url = f"{self.url}/api/v2/signage"
