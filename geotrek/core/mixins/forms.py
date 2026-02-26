from geotrek.common.forms import CommonForm
from geotrek.core.fields import TopologyField


class TopologyForm(CommonForm):
    """
    This form is a bit specific :

        We use an extra field (topology) in order to edit the whole model instance.
        The whole instance, because we use concrete inheritance for topology models.
        Thus, at init, we load the instance into field, and at save, we
        save the field into the instance.

    The geom field is fully ignored, since we edit a topology.
    """

    topology = TopologyField(label="")

    geomfields = ["topology"]

    class Meta(CommonForm.Meta):
        fields = [*CommonForm.Meta.fields, "topology"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["topology"].initial = self.instance

    def clean(self, *args, **kwargs):
        data = super().clean()
        # geom is computed at db-level and never edited
        if "geom" in self.errors:
            del self.errors["geom"]
        return data

    def save(self, *args, **kwargs):
        topology = self.cleaned_data.pop("topology")
        instance = super().save(*args, **kwargs)
        was_edited = instance.pk != topology.pk
        if was_edited:
            instance.mutate(topology)
        return instance
