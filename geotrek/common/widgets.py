from datetime import datetime
from django.utils.translation import ugettext_lazy as _
from django.forms.widgets import Select


class YearSelect(Select):
    label = _('Any year')

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = self._get_choices()
        super(YearSelect, self).__init__(*args, **kwargs)

    def _get_choices(self):
        years_range = [(-1, self.label)]
        years_range += [(year, year) for year in self.get_years()]
        return years_range

    def get_years(self):
        return list(range(datetime.today().year, 1979, -1))

    def render_options(self, *args, **kwargs):
        """Refresh choices each time the form is rendered.
        (Prevents from having to restart the application on 1st of January
         to see current year for example)
        """
        self.choices = self._get_choices()
        return super(YearSelect, self).render_options(*args, **kwargs)


class ValueSelect(Select):
    label = _('Any value')

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = self._get_choices()
        super(ValueSelect, self).__init__(*args, **kwargs)

    def _get_choices(self):
        values_range = [(-1, self.label)]
        values_range += [(value, value) for value in self.get_values()]
        return values_range

    def get_values(self):
        """
        Must be overridden
        """
        return []

    def render_options(self, *args, **kwargs):
        """Refresh choices each time the form is rendered.
        (Prevents from having to restart the application on 1st of January
         to see current year for example)
        """
        self.choices = self._get_choices()
        return super(ValueSelect, self).render_options(*args, **kwargs)
