from geotrek.common.models import Organism
from geotrek.common.parsers import ExcelParser


class CustomParser(ExcelParser):
    model = Organism
    fields = {"organism": "nOm"}
