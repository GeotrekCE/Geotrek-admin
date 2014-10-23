from .models import TouristicContent, TouristicEvent
from geotrek.common.forms import CommonForm


class TouristicContentForm(CommonForm):
    geomfields = ['geom']

    class Meta:
        fields = ['name', 'category', 'type1', 'type2', 'published',
                  'description_teaser', 'description', 'themes', 'contact',
                  'email', 'website', 'practical_info', 'geom']
        model = TouristicContent

    def __init__(self, *args, **kwargs):
        super(TouristicContentForm, self).__init__(*args, **kwargs)
        self.fields['type1'].help_text = ''
        self.fields['type2'].help_text = ''


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
