import json
import os


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


class GeotrekParserTestMixin:
    def mock_json(self):
        filename = os.path.join('geotrek', self.mock_json_order[self.mock_time][0], 'tests', 'data', 'geotrek_parser_v2',
                                self.mock_json_order[self.mock_time][1])
        self.mock_time += 1
        with open(filename, 'r') as f:
            return json.load(f)
