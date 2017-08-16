from geotrek.common.serializers import BasePublishableSerializerMixin, PictogramSerializerMixin, TranslatedModelSerializer
from geotrek.sensitivity import models as sensitivity_models


class SportPracticeSerializer(TranslatedModelSerializer):
    class Meta:
        model = sensitivity_models.SportPractice
        fields = ('id', 'name')


class SpeciesSerializer(TranslatedModelSerializer, PictogramSerializerMixin):
    practices = SportPracticeSerializer(many=True)

    class Meta:
        model = sensitivity_models.Species
        fields = ['id', 'name', 'practices', 'url', 'pictogram'] + ['period{:02}'.format(p) for p in range(1, 13)]


class SensitiveAreaSerializer(BasePublishableSerializerMixin, TranslatedModelSerializer):
    species = SpeciesSerializer()

    class Meta:
        model = sensitivity_models.SensitiveArea
        geo_field = 'geom'
        fields = ('id', 'species') + BasePublishableSerializerMixin.Meta.fields
