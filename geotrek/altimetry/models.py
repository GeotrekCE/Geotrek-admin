import os

from django.conf import settings
from django.contrib.gis.db import models
from django.utils.translation import get_language, ugettext_lazy as _
from django.template.defaultfilters import floatformat

from mapentity.helpers import is_file_newer, convertit_download, smart_urljoin
from .helpers import AltimetryHelper


class AltimetryMixin(models.Model):
    # Computed values (managed at DB-level with triggers)
    geom_3d = models.GeometryField(dim=3, srid=settings.SRID, spatial_index=False,
                                   editable=False, null=True, default=None)
    length = models.FloatField(editable=False, default=0.0, null=True, blank=True, db_column='longueur',
                               verbose_name=_(u"3D Length"))
    ascent = models.IntegerField(editable=False, default=0, null=True, blank=True,
                                 db_column='denivelee_positive', verbose_name=_(u"Ascent"))
    descent = models.IntegerField(editable=False, default=0, null=True, blank=True,
                                  db_column='denivelee_negative', verbose_name=_(u"Descent"))
    min_elevation = models.IntegerField(editable=False, default=0, null=True, blank=True,
                                        db_column='altitude_minimum', verbose_name=_(u"Minimum elevation"))
    max_elevation = models.IntegerField(editable=False, default=0, null=True, blank=True,
                                        db_column='altitude_maximum', verbose_name=_(u"Maximum elevation"))
    slope = models.FloatField(editable=False, null=True, blank=True, default=0.0,
                              verbose_name=_(u"Slope"), db_column='pente')

    COLUMNS = ['length', 'ascent', 'descent', 'min_elevation', 'max_elevation', 'slope']

    class Meta:
        abstract = True

    @property
    def length_display(self):
        return floatformat(self.length)

    def reload(self, fromdb=None):
        """Reload fields computed at DB-level (triggers)
        """
        if fromdb is None:
            fromdb = self.__class__.objects.get(pk=self.pk)
        self.geom_3d = fromdb.geom_3d
        self.length = fromdb.length
        self.ascent = fromdb.ascent
        self.descent = fromdb.descent
        self.min_elevation = fromdb.min_elevation
        self.max_elevation = fromdb.max_elevation
        self.slope = fromdb.slope
        return self

    def get_elevation_profile(self):
        return AltimetryHelper.elevation_profile(self.geom_3d)

    def get_elevation_area(self):
        return AltimetryHelper.elevation_area(self.geom)

    def get_elevation_limits(self):
        return AltimetryHelper.altimetry_limits(self.get_elevation_profile())

    def get_elevation_profile_svg(self):
        return AltimetryHelper.profile_svg(self.get_elevation_profile())

    @models.permalink
    def get_elevation_chart_url(self):
        """Generic url. Will fail if there is no such url defined
        for the required model (see core.Path and trekking.Trek)
        """
        app_label = self._meta.app_label
        model_name = self._meta.model_name
        return ('%s:%s_profile_svg' % (app_label, model_name), [], {'lang': get_language(), 'pk': self.pk})

    def get_elevation_chart_path(self, language):
        """Path to the PNG version of elevation chart.
        """
        basefolder = os.path.join(settings.MEDIA_ROOT, 'profiles')
        if not os.path.exists(basefolder):
            os.mkdir(basefolder)
        return os.path.join(basefolder, '%s-%s-%s.png' % (self._meta.model_name, self.pk, language))

    def prepare_elevation_chart(self, language, rooturl):
        """Converts SVG elevation URI to PNG on disk.
        """
        from .views import HttpSVGResponse
        path = self.get_elevation_chart_path(language)
        # Do nothing if image is up-to-date
        if is_file_newer(path, self.date_update):
            return False
        # Download converted chart as png using convertit
        source = smart_urljoin(rooturl, self.get_elevation_chart_url())
        convertit_download(source,
                           path,
                           from_type=HttpSVGResponse.content_type,
                           to_type='image/png',
                           headers={'Accept-Language': language})
        return True
