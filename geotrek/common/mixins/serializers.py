from mapentity.serializers.fields import MapentityDateTimeField


class TimeStampedModelSerializerMixin:
    date_update = MapentityDateTimeField()
    date_insert = MapentityDateTimeField()

    class Meta:
        fields = ('date_update', 'date_insert', )
