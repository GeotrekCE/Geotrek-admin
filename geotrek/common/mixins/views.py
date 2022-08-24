import os
from io import BytesIO
from urllib.parse import urljoin

from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.utils.functional import classproperty
from django.utils.translation import gettext as _
from django.views import static
from mapentity import views as mapentity_views
from mapentity.helpers import suffix_for
from pdfimpose import PageList

from geotrek.common.models import TargetPortal, FileType, Attachment
from geotrek.common.utils import logger
from geotrek.common.utils.portals import smart_get_template_by_portal

from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response


class CustomColumnsMixin:
    """ Customize columns in List views """

    _MAP_SETTINGS = {
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
        'BladeList': 'blade_view',
        'BladeJsonList': 'blade_view',
        'BladeFormatList': 'blade_export',
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

    @classmethod
    def get_mandatory_columns(cls):
        mandatory_cols = getattr(cls, 'mandatory_columns', None)
        if (mandatory_cols is None):
            logger.error(
                f"Cannot build columns for class {cls.__name__}.\n"
                + "Please define on this class either : \n"
                + "  - a field 'columns'\n"  # If we ended up here, then we know 'columns' is not defined higher in the MRO
                + "OR \n"
                + "  - two fields 'mandatory_columns' AND 'default_extra_columns'"
            )
        return mandatory_cols

    @classmethod
    def get_default_extra_columns(cls):
        default_extra_columns = getattr(cls, 'default_extra_columns', None)
        if (default_extra_columns is None):
            logger.error(
                f"Cannot build columns for class {cls.__name__}.\n"
                + "Please define on this class either : \n"
                + "  - a field 'columns'\n"  # If we ended up here, then we know 'columns' is not defined higher in the MRO
                + "OR \n"
                + "  - two fields 'mandatory_columns' AND 'default_extra_columns'"
            )
        return default_extra_columns

    @classmethod
    def get_custom_columns(cls):
        settings_key = cls._MAP_SETTINGS.get(cls.__name__, '')
        return settings.COLUMNS_LISTS.get(settings_key, [])

    @classproperty
    def columns(cls):
        mandatory_cols = cls.get_mandatory_columns()
        default_extra_cols = cls.get_default_extra_columns()
        if mandatory_cols is None or default_extra_cols is None:
            return []
        else:
            # Get extra columns names from instance settings, or use default extra columns
            extra_columns = cls.get_custom_columns() or default_extra_cols
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


class MetaMixin:
    def get_context_data(self, **kwargs):
        lang = self.request.GET.get('lang')
        portal = self.request.GET.get('portal')
        context = super().get_context_data(**kwargs)
        context['FACEBOOK_APP_ID'] = settings.FACEBOOK_APP_ID
        context['FACEBOOK_IMAGE'] = urljoin(self.request.GET['rando_url'], settings.FACEBOOK_IMAGE)
        context['FACEBOOK_IMAGE_WIDTH'] = settings.FACEBOOK_IMAGE_WIDTH
        context['FACEBOOK_IMAGE_HEIGHT'] = settings.FACEBOOK_IMAGE_HEIGHT
        translation.activate(lang)
        context['META_TITLE'] = _('Geotrek Rando')
        translation.deactivate()
        if portal:
            try:
                target_portal = TargetPortal.objects.get(name=portal)
                context['FACEBOOK_APP_ID'] = target_portal.facebook_id
                context['FACEBOOK_IMAGE'] = urljoin(self.request.GET['rando_url'], target_portal.facebook_image_url)
                context['FACEBOOK_IMAGE_WIDTH'] = target_portal.facebook_image_width
                context['FACEBOOK_IMAGE_HEIGHT'] = target_portal.facebook_image_height
                context['META_TITLE'] = getattr(target_portal, 'title_{}'.format(lang))
            except TargetPortal.DoesNotExist:
                pass
        return context


class DocumentPortalMixin:
    def get_context_data(self, **kwargs):

        portal = self.request.GET.get('portal')
        if portal:
            suffix = suffix_for(self.template_name_suffix, "_pdf", "html")

            template_portal = smart_get_template_by_portal(self.model, portal, suffix)
            if template_portal:
                self.template_name = template_portal

            template_css_portal = smart_get_template_by_portal(self.model, portal,
                                                               suffix_for(self.template_name_suffix, "_pdf", "css"))
            if template_css_portal:
                self.template_css = template_css_portal
        context = super().get_context_data(**kwargs)
        return context


class DocumentPublicMixin:
    template_name_suffix = "_public"

    # Override view_permission_required
    def dispatch(self, *args, **kwargs):
        return super(mapentity_views.MapEntityDocumentBase, self).dispatch(*args, **kwargs)

    def get(self, request, pk, slug, lang=None):
        obj = get_object_or_404(self.model, pk=pk)
        try:
            file_type = FileType.objects.get(type="Topoguide")
        except FileType.DoesNotExist:
            file_type = None
        attachments = Attachment.objects.attachments_for_object_only_type(obj, file_type)
        if not attachments and not settings.ONLY_EXTERNAL_PUBLIC_PDF:
            return super().get(request, pk, slug, lang)
        if not attachments:
            return HttpResponseNotFound("No attached file with 'Topoguide' type.")
        path = attachments[0].attachment_file.name

        if settings.DEBUG:
            response = static.serve(self.request, path, settings.MEDIA_ROOT)
        else:
            response = HttpResponse()
            response[settings.MAPENTITY_CONFIG['SENDFILE_HTTP_HEADER']] = os.path.join(settings.MEDIA_URL_SECURE, path)
        response["Content-Type"] = 'application/pdf'
        response['Content-Disposition'] = "attachment; filename={0}.pdf".format(slug)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        modelname = self.get_model()._meta.object_name.lower()
        context['mapimage_ratio'] = settings.EXPORT_MAP_IMAGE_SIZE[modelname]
        return context


class CompletenessMixin:
    """Mixin for completeness fields"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        modelname = self.get_model()._meta.object_name.lower()
        if modelname in settings.COMPLETENESS_FIELDS:
            obj = context['object']
            completeness_fields = settings.COMPLETENESS_FIELDS[modelname]
            context['completeness_fields'] = [obj._meta.get_field(field).verbose_name for field in completeness_fields]
        return context


class DuplicateMixin:
    @action(methods=['POST'], detail=False, renderer_classes=[JSONRenderer])
    def duplicate_object(self, request, *args, **kwargs):
        try:
            model_name = self.model._meta.model_name
            app_name = self.model._meta.app_label
            ids_duplicate = request.POST.getlist(f'{model_name}[]')
            objects = self.model.objects.filter(pk__in=ids_duplicate)
            if not request.user.has_perm(f'{app_name}.change_{model_name}'):
                raise Exception(f'''{_("You don't have the right to duplicate these ")}{self.model._meta.verbose_name_plural}''')
            errors_obj = []
            for obj in objects:
                if hasattr(obj, 'same_structure') and not (obj.same_structure(request.user) and request.user.has_perm('authent.can_bypass_structure')):
                    errors_obj.append(str(obj.pk))
                else:
                    obj.duplicate()
            if errors_obj:
                raise Exception(
                    f'''{_("You don't have the right to duplicate these ")}
                        {self.model._meta.verbose_name_plural} id : {", ".join(errors_obj)},
                        this object is not from the same structure.''')
            response = {'success': _("Duplicated successfully")}
        except Exception as exc:
            response = {'error': '%s' % exc, }
        return Response(response)


class DuplicateListMixin:
    def get_context_data(self):
        context = super().get_context_data()
        model = self.get_model()
        context['duplicate_object'] = f'{model._meta.app_label}:{model._meta.model_name}-drf-duplicate-object'
        return context
