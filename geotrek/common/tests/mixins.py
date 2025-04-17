import json
import os

from geotrek.common.parsers import DownloadImportError


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


class GeotrekParserTestMixin:
    def mock_json(self):
        filename = os.path.join(
            "geotrek",
            self.mock_json_order[self.mock_time][0],
            "tests",
            "data",
            "geotrek_parser_v2",
            self.mock_json_order[self.mock_time][1],
        )
        self.mock_time += 1
        if (
            "trek_not_found" in filename
            or "trek_unpublished_practice_not_found" in filename
        ):
            msg = "404 Does not exist"
            raise DownloadImportError(msg)
        with open(filename) as f:
            return json.load(f)
