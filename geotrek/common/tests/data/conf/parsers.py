from geotrek.common.models import Organism
from geotrek.common.tests.test_parsers import JSONParser


class CustomParser(JSONParser):
    model = Organism
    fields = {"organism": "nom"}
