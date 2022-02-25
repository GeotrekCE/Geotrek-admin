from io import BytesIO

from django.conf import settings
from pdfimpose import PageList

from geotrek.common.utils import logger


class CustomColumnsMixin:
    """ Customize columns in List views """

    MAP_SETTINGS = {
        'PathList': 'path_view',
        'PathJsonList': 'path_view',
        'PathFormatList': 'path_export',
        'TrailList': 'trail_view',
        'TrailJsonList': 'trail_view',
        'TrailFormatList': 'trail_export',
        'LandEdgeList': 'landedge_view',
        'LandEdgeJsonList': 'landedge_view',
        'LandEdgeFormatList': 'landedge_export',
        'PhysicalEdgeList': 'physicaledge_view',
        'PhysicalEdgeJsonList': 'physicaledge_view',
        'PhysicalEdgeFormatList': 'physicaledge_export',
        'CompetenceEdgeList': 'competenceedge_view',
        'CompetenceEdgeJsonList': 'competenceedge_view',
        'CompetenceEdgeFormatList': 'competenceedge_export',
        'SignageManagementEdgeList': 'signagemanagementedge_view',
        'SignageManagementEdgeJsonList': 'signagemanagementedge_view',
        'SignageManagementEdgeFormatList': 'signagemanagementedge_export',
        'WorkManagementEdgeList': 'workmanagementedge_view',
        'WorkManagementEdgeJsonList': 'workmanagementedge_view',
        'WorkManagementEdgeFormatList': 'workmanagementedge_export',
        'InfrastructureList': 'infrastructure_view',
        'InfrastructureJsonList': 'infrastructure_view',
        'InfrastructureFormatList': 'infrastructure_export',
        'SignageList': 'signage_view',
        'SignageJsonList': 'signage_view',
        'SignageFormatList': 'signage_export',
        'InterventionList': 'intervention_view',
        'InterventionJsonList': 'intervention_view',
        'InterventionFormatList': 'intervention_export',
        'ProjectList': 'project_view',
        'ProjectJsonList': 'project_view',
        'ProjectFormatList': 'project_export',
        'TrekList': 'trek_view',
        'TrekJsonList': 'trek_view',
        'TrekFormatList': 'trek_export',
        'POIList': 'poi_view',
        'POIJsonList': 'poi_view',
        'POIFormatList': 'poi_export',
        'ServiceList': 'service_view',
        'ServiceJsonList': 'service_view',
        'ServiceFormatList': 'service_export',
        'DiveList': 'dive_view',
        'DiveJsonList': 'dive_view',
        'DiveFormatList': 'dive_export',
        'TouristicContentList': 'touristic_content_view',
        'TouristicContentJsonList': 'touristic_content_view',
        'TouristicContentFormatList': 'touristic_content_export',
        'TouristicEventList': 'touristic_event_view',
        'TouristicEventJsonList': 'touristic_event_view',
        'TouristicEventFormatList': 'touristic_event_export',
        'ReportList': 'feedback_view',
        'ReportJsonList': 'feedback_view',
        'ReportFormatList': 'feedback_export',
        'SensitiveAreaList': 'sensitivity_view',
        'SensitiveAreaJsonList': 'sensitivity_view',
        'SensitiveAreaFormatList': 'sensitivity_export',
        'SiteList': 'outdoor_site_view',
        'SiteJsonList': 'outdoor_site_view',
        'SiteFormatList': 'outdoor_site_export',
        'CourseList': 'outdoor_course_view',
        'CourseJsonList': 'outdoor_course_view',
        'CourseFormatList': 'outdoor_course_export',
    }

    def get_mandatory_columns(self):
        mandatory_cols = getattr(self, 'mandatory_columns', None)
        if (mandatory_cols is None):
            logger.error(
                f"Cannot build columns for class {self.__class__.__name__}.\n"
                + "Please define on this class either : \n"
                + "  - a field 'columns'\n"  # If we ended up here, then we know 'columns' is not defined higher in the MRO
                + "OR \n"
                + "  - two fields 'mandatory_columns' AND 'default_extra_columns'"
            )
        return mandatory_cols

    def get_default_extra_columns(self):
        default_extra_columns = getattr(self, 'default_extra_columns', None)
        if (default_extra_columns is None):
            logger.error(
                f"Cannot build columns for class {self.__class__.__name__}.\n"
                + "Please define on this class either : \n"
                + "  - a field 'columns'\n"  # If we ended up here, then we know 'columns' is not defined higher in the MRO
                + "OR \n"
                + "  - two fields 'mandatory_columns' AND 'default_extra_columns'"
            )
        return default_extra_columns

    @property
    def columns(self):
        mandatory_cols = self.get_mandatory_columns()
        default_extra_cols = self.get_default_extra_columns()
        settings_key = self.MAP_SETTINGS.get(self.__class__.__name__, '')
        if (mandatory_cols is None or default_extra_cols is None):
            return []
        else:
            # Get extra columns names from instance settings, or use default extra columns
            extra_columns = settings.COLUMNS_LISTS.get(settings_key, default_extra_cols)
            # Some columns are mandatory to prevent crashes
            columns = mandatory_cols + extra_columns
            return columns


class BookletMixin:
    def get(self, request, pk, slug, lang=None):
        response = super().get(request, pk, slug)
        response.add_post_render_callback(transform_pdf_booklet_callback)
        return response


def transform_pdf_booklet_callback(response):
    content = response.content
    content_b = BytesIO(content)
    import pdfimpose

    pages = PageList([content_b])
    for x in pages:
        x.pdf.strict = False
    new_pdf = pdfimpose._legacy_pypdf_impose(
        matrix=pdfimpose.ImpositionMatrix([pdfimpose.Direction.horizontal], 'left'),
        pages=pages,
        last=0
    )
    result = BytesIO()
    new_pdf.write(result)
    response.content = result.getvalue()
