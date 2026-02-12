from django.db.models import BooleanField
from django.db.models.expressions import Func

class TopologyIsValid(Func):
    function = "TopologyIsValid"
    arity = 1
    output_field = BooleanField()
