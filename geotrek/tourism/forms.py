from geotrek.common.forms import CommonForm

from .models import TouristicContent, TouristicEvent


class TouristicContentForm(CommonForm):
    geomfields = ['geom']

    class Meta:
        fields = ['name', 'published', 'description_teaser', 'description',
                  'themes', 'category', 'contact', 'email', 'website',
                  'practical_info', 'geom']
        model = TouristicContent


class TouristicEventForm(CommonForm):
    geomfields = ['geom']

    class Meta:
        fields = ['name', 'published', 'description_teaser', 'description',
                  'themes', 'begin_date', 'end_date', 'duration',
                  'meeting_point', 'meeting_time', 'contact', 'email',
                  'website', 'organizer', 'speaker', 'usage', 'accessibility',
                  'participant_number', 'booking', 'public', 'practical_info',
                  'geom']
        model = TouristicEvent
