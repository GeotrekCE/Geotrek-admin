from geotrek.common.serializers import (ThemeSerializer, PublishableSerializerMixin,
                                        PictogramSerializerMixin, RecordSourceSerializer,
                                        PicturesSerializerMixin, TranslatedModelSerializer,
                                        TargetPortalSerializer)
from geotrek.diving import models as diving_models


class DifficultySerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = diving_models.Difficulty
        fields = ('id', 'pictogram', 'name')


class LevelSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = diving_models.Difficulty
        fields = ('id', 'pictogram', 'name', 'description')


class PracticeSerializer(PictogramSerializerMixin, TranslatedModelSerializer):
    class Meta:
        model = diving_models.Difficulty
        fields = ('id', 'pictogram', 'name')


class DiveSerializer(PicturesSerializerMixin, PublishableSerializerMixin,
                     TranslatedModelSerializer):
    themes = ThemeSerializer(many=True)
    practice = PracticeSerializer()
    difficulty = DifficultySerializer()
    levels = LevelSerializer(many=True)
    source = RecordSourceSerializer(many=True)
    portal = TargetPortalSerializer(many=True)

    class Meta:
        model = diving_models.Dive
        geo_field = 'geom'
        fields = (
            'id', 'practice', 'description_teaser', 'description', 'advice',
            'difficulty', 'levels', 'themes', 'owner', 'depth',
            'facilities', 'departure', 'disabled_sport',
            'source', 'portal', 'eid',
        ) + PublishableSerializerMixin.Meta.fields + PicturesSerializerMixin.Meta.fields
