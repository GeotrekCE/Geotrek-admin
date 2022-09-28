from datetime import datetime


from datetime import datetime

from django.utils.translation import gettext_lazy as _

from .models import TouristicContent, TouristicEvent
from geotrek.common.forms import CommonForm

from crispy_forms.layout import Div


class TouristicContentForm(CommonForm):
    geomfields = ['geom']

    fieldslayout = [
        Div(
            'structure',
            'name',
            'category',
            'type1',
            'type2',
            'review',
            'published',
            'approved',
            'description_teaser',
            'description',
            'themes',
            'contact',
            'email',
            'website',
            'practical_info',
            'accessibility',
            'label_accessibility',
            'source',
            'portal',
            'eid',
            'reservation_system',
            'reservation_id'
        )
    ]

    class Meta:
        fields = ['structure', 'name', 'category', 'type1', 'type2', 'review', 'published',
                  'description_teaser', 'description', 'themes', 'contact',
                  'email', 'website', 'practical_info', 'accessibility', 'label_accessibility', 'approved', 'source',
                  'portal', 'geom', 'eid', 'reservation_system', 'reservation_id']
        model = TouristicContent

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Since we use chosen() in trek_form.html, we don't need the default help text
        for f in ['themes', 'type1', 'type2', 'source', 'portal']:
            self.fields[f].help_text = ''


class TouristicEventForm(CommonForm):
    geomfields = ['geom']

    fieldslayout = [
        Div(
            'structure',
            'name',
            'review',
            'published',
            'description_teaser',
            'description',
            'themes',
            'begin_date',
            'end_date',
            'duration',
            'meeting_point',
            'start_time',
            'end_time',
            'contact',
            'email',
            'website',
            'organizer',
            'speaker',
            'type',
            'accessibility',
            'participant_number',
            'booking',
            'target_audience',
            'practical_info',
            'approved',
            'source',
            'portal',
            'eid',
        )
    ]

    class Meta:
        fields = ['name', 'review', 'published', 'description_teaser', 'description',
                  'themes', 'begin_date', 'end_date', 'duration', 'meeting_point',
                  'start_time', 'end_time', 'contact', 'email', 'website', 'organizer', 'speaker',
                  'type', 'accessibility', 'participant_number', 'booking', 'target_audience',
                  'practical_info', 'approved', 'source', 'portal', 'geom', 'eid', 'structure']
        model = TouristicEvent

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['begin_date'].widget.attrs['placeholder'] = _('dd/mm/yyyy')
        self.fields['end_date'].widget.attrs['placeholder'] = _('dd/mm/yyyy')
        self.fields['start_time'].widget.attrs['placeholder'] = _('HH:MM')
        self.fields['end_time'].widget.attrs['placeholder'] = _('HH:MM')
        # Since we use chosen() in trek_form.html, we don't need the default help text
        for f in ['themes', 'source']:
            self.fields[f].help_text = ''

    def clean(self, *args, **kwargs):
        clean_data = super().clean(*args, **kwargs)
        start_time = clean_data.get('start_time')
        end_time = clean_data.get('end_time')
        if not start_time and not end_time:
            pass
        elif not start_time and end_time:
            self.add_error('start_time', _('Start time is unset'))
        elif not end_time:
            pass
        elif not clean_data.get('end_date'):
            if start_time > end_time:
                self.add_error('end_time', _('Start time is after end time'))
        else:
            begin = datetime.combine(clean_data.get('begin_date'), start_time)
            end = datetime.combine(clean_data.get('end_date'), end_time)
            if begin > end:
                self.add_error('end_time', _('Start time is after end time'))

        return clean_data
