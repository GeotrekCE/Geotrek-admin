from geotrek.common.parsers import GeotrekParser
from geotrek.signage.models import Signage


class GeotrekSignageParser(GeotrekParser):
    url = None
    model = Signage
    constant_fields = {
        "published": True,
        "deleted": False
    }
    replace_fields = {
        "eid": "uuid",
        "geom": "geometry"
    }
    url_categories = {
        'sealing': '/api/v2/signage_sealing/',
        'condition': '/api/v2/infrastructure_condition/',
        'type': '/api/v2/signage_type/',
    }
    categories_keys_api_v2 = {
        'condition': 'label',
        'sealing': 'label',
        'type': 'label'
    }
    natural_keys = {
        'condition': 'label',
        'sealing': 'label',
        'type': 'label'
    }

    def next_row(self):
        self.next_url = f"{self.url}/api/v2/signage"
        return super().next_row()
