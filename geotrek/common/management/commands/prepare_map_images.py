from geotrek.common.mixins import NoDeleteMixin
from mapentity.management.commands.prepare_map_images import Command as MapentityCommand


class Command(MapentityCommand):
    """Override mapentity command of the same name to exclude deleted objects."""

    def get_instances(self, model):
        if issubclass(model, NoDeleteMixin):
            return model.objects.existing()
        else:
            return model.objects.all()
