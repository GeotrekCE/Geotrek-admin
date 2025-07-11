import json
import os
from io import BytesIO

import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.utils.functional import classproperty
from django.utils.translation import gettext as _
from django.views import static
from django.views.generic import DetailView, FormView
from mapentity import views as mapentity_views
from mapentity.helpers import suffix_for
from pdfimpose.schema.saddle import impose
from pymupdf import Document

from geotrek.authent.models import UserProfile
from geotrek.common.forms import OSMForm
from geotrek.common.models import Attachment, FileType
from geotrek.common.utils import logger
from geotrek.common.utils.openstreetmap_api import (
    close_changeset,
    create_changeset,
    get_element,
    get_osm_oauth_uri,
    update_element,
)
from geotrek.common.utils.portals import smart_get_template_by_portal
from geotrek.common.utils.translation import get_translated_fields


class CustomColumnsMixin:
    """Customize columns in List views"""

    _MAP_SETTINGS = {
        "PathList": "path_view",
        "PathJsonList": "path_view",
        "PathFormatList": "path_export",
        "TrailList": "trail_view",
        "TrailJsonList": "trail_view",
        "TrailFormatList": "trail_export",
        "LandEdgeList": "landedge_view",
        "LandEdgeJsonList": "landedge_view",
        "LandEdgeFormatList": "landedge_export",
        "PhysicalEdgeList": "physicaledge_view",
        "PhysicalEdgeJsonList": "physicaledge_view",
        "PhysicalEdgeFormatList": "physicaledge_export",
        "CirculationEdgeList": "circulationedge_view",
        "CirculationEdgeJsonList": "circulationedge_view",
        "CirculationEdgeFormatList": "circulationedge_export",
        "CompetenceEdgeList": "competenceedge_view",
        "CompetenceEdgeJsonList": "competenceedge_view",
        "CompetenceEdgeFormatList": "competenceedge_export",
        "SignageManagementEdgeList": "signagemanagementedge_view",
        "SignageManagementEdgeJsonList": "signagemanagementedge_view",
        "SignageManagementEdgeFormatList": "signagemanagementedge_export",
        "WorkManagementEdgeList": "workmanagementedge_view",
        "WorkManagementEdgeJsonList": "workmanagementedge_view",
        "WorkManagementEdgeFormatList": "workmanagementedge_export",
        "InfrastructureList": "infrastructure_view",
        "InfrastructureJsonList": "infrastructure_view",
        "InfrastructureFormatList": "infrastructure_export",
        "SignageList": "signage_view",
        "SignageJsonList": "signage_view",
        "SignageFormatList": "signage_export",
        "BladeList": "blade_view",
        "BladeJsonList": "blade_view",
        "BladeFormatList": "blade_export",
        "InterventionList": "intervention_view",
        "InterventionJsonList": "intervention_view",
        "InterventionFormatList": "intervention_export",
        "ProjectList": "project_view",
        "ProjectJsonList": "project_view",
        "ProjectFormatList": "project_export",
        "TrekList": "trek_view",
        "TrekJsonList": "trek_view",
        "TrekFormatList": "trek_export",
        "POIList": "poi_view",
        "POIJsonList": "poi_view",
        "POIFormatList": "poi_export",
        "ServiceList": "service_view",
        "ServiceJsonList": "service_view",
        "ServiceFormatList": "service_export",
        "DiveList": "dive_view",
        "DiveJsonList": "dive_view",
        "DiveFormatList": "dive_export",
        "TouristicContentList": "touristic_content_view",
        "TouristicContentJsonList": "touristic_content_view",
        "TouristicContentFormatList": "touristic_content_export",
        "TouristicEventList": "touristic_event_view",
        "TouristicEventJsonList": "touristic_event_view",
        "TouristicEventFormatList": "touristic_event_export",
        "ReportList": "feedback_view",
        "ReportJsonList": "feedback_view",
        "ReportFormatList": "feedback_export",
        "SensitiveAreaList": "sensitivity_view",
        "SensitiveAreaJsonList": "sensitivity_view",
        "SensitiveAreaFormatList": "sensitivity_export",
        "SiteList": "outdoor_site_view",
        "SiteJsonList": "outdoor_site_view",
        "SiteFormatList": "outdoor_site_export",
        "CourseList": "outdoor_course_view",
        "CourseJsonList": "outdoor_course_view",
        "CourseFormatList": "outdoor_course_export",
    }

    @classmethod
    def get_mandatory_columns(cls):
        mandatory_cols = getattr(cls, "mandatory_columns", None)
        if mandatory_cols is None:
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
        default_extra_columns = getattr(cls, "default_extra_columns", None)
        if default_extra_columns is None:
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
        settings_key = cls._MAP_SETTINGS.get(cls.__name__, "")
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

    result = BytesIO()

    impose(
        files=[Document(stream=content_b)],
        output=result,
        folds="h",
    )

    response.content = result.getvalue()


class DocumentPortalMixin:
    def get_context_data(self, **kwargs):
        portal = self.request.GET.get("portal")
        if portal:
            suffix = suffix_for(self.template_name_suffix, "_pdf", "html")

            template_portal = smart_get_template_by_portal(self.model, portal, suffix)
            if template_portal:
                self.template_name = template_portal

            template_css_portal = smart_get_template_by_portal(
                self.model, portal, suffix_for(self.template_name_suffix, "_pdf", "css")
            )
            if template_css_portal:
                self.template_css = template_css_portal
        context = super().get_context_data(**kwargs)
        return context


class DocumentPublicMixin:
    template_name_suffix = "_public"

    # Override view_permission_required
    def dispatch(self, *args, **kwargs):
        return super(mapentity_views.MapEntityDocumentBase, self).dispatch(
            *args, **kwargs
        )

    def get(self, request, pk, slug, lang=None):
        obj = get_object_or_404(self.model, pk=pk)
        try:
            file_type = FileType.objects.get(type="Topoguide")
        except FileType.DoesNotExist:
            file_type = None
        attachments = Attachment.objects.attachments_for_object_only_type(
            obj, file_type
        )
        if not attachments and not settings.ONLY_EXTERNAL_PUBLIC_PDF:
            return super().get(request, pk, slug, lang)
        if not attachments:
            return HttpResponseNotFound("No attached file with 'Topoguide' type.")
        path = attachments[0].attachment_file.name

        if settings.DEBUG:
            response = static.serve(self.request, path, settings.MEDIA_ROOT)
        else:
            response = HttpResponse()
            response[settings.MAPENTITY_CONFIG["SENDFILE_HTTP_HEADER"]] = os.path.join(
                settings.MEDIA_URL_SECURE, path
            )
        response["Content-Type"] = "application/pdf"
        response["Content-Disposition"] = f"attachment; filename={slug}.pdf"
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        modelname = self.get_model()._meta.object_name.lower()
        context["mapimage_ratio"] = settings.EXPORT_MAP_IMAGE_SIZE[modelname]
        return context


class CompletenessMixin:
    """Mixin for completeness fields"""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        modelname = self.get_model()._meta.object_name.lower()
        if modelname in settings.COMPLETENESS_FIELDS:
            obj = context["object"]
            completeness_fields = settings.COMPLETENESS_FIELDS[modelname]
            context["completeness_fields"] = [
                obj._meta.get_field(field).verbose_name for field in completeness_fields
            ]
        return context


class OSMDetailMixin:
    """
    Mixin for detail views integrating OpenStreetMap comparison functionality.

    Manages OSM comparison button display based on the following conditions:
    - Requires OSM configuration (OSM_CLIENT_ID, OSM_CLIENT_SECRET, OSM_APPLICATION_NAME)
    - If user has OSM token: redirects to comparison page
    - If no token but OSM configured: redirects to OSM authorization
    - If OSM not configured or provider name doesn't start with "OpenStreetMap": button hidden
    """

    def get_osm_context_data(self):
        app_name = self.get_model()._meta.app_label.lower()
        model = self.get_model()._meta.verbose_name.lower()

        user_id = self.request.user.id
        token = UserProfile.objects.get(user_id=user_id).osm_token
        osm_configured = all(
            hasattr(settings, key)
            for key in ("OSM_CLIENT_ID", "OSM_CLIENT_SECRET", "OSM_APPLICATION_NAME")
        )

        if token:
            redirect_url = reverse(
                f"{app_name}:{model}_osm_compare", args=[self.object.pk]
            )

        elif osm_configured:
            redirect_uri = self.request.build_absolute_uri(
                reverse("common:osm_authorize")
            )
            uri, state = get_osm_oauth_uri(redirect_uri)

            # save information to be able to redirect the user on the comparison page after OSM connexion
            self.request.session["osm_state"] = state
            self.request.session["object_id"] = self.object.pk
            self.request.session["object_model"] = model
            self.request.session["object_app"] = app_name

            redirect_url = uri
        else:
            redirect_url = ""

        return {
            "osm_redirect_url": redirect_url,
            "osm_user_credential_available": osm_configured,
            "infotip": not (token),
        }


class OSMComparisonViewMixin(DetailView):
    """
    Mixin for detail views that handles field mapping comparison between Geotrek and OpenStreetMap.

    Fetches OSM objects via the OpenStreetMap API v0.6 and compares field values based on a mapping
    configuration defined in the main view. Handles field translations and displays side-by-side
    comparison for validation purposes.
    """

    template_name = "common/osm_comparison.html"

    type_map = {"N": "node", "W": "way", "R": "relation"}
    osm_object = None

    def translation(self):
        default_lang = settings.MODELTRANSLATION_DEFAULT_LANGUAGE

        for field in get_translated_fields(self.model):
            osm_keys = self.mapping.get(field)
            if not osm_keys:
                continue

            is_str = isinstance(osm_keys, str)
            osm_keys = [osm_keys] if is_str else list(osm_keys)

            # Protect the class from multiple translation mappings as field is a static attribute
            is_translated = [
                tag for tag in osm_keys if tag.endswith(f":{default_lang}")
            ]
            if is_translated:
                continue

            for lang in settings.MODELTRANSLATION_LANGUAGES:
                if lang != default_lang:
                    geotrek_field = f"{field}_{lang}"
                    translated = [tag + ":" + lang for tag in osm_keys]
                    self.mapping[geotrek_field] = (
                        translated[0] if is_str else tuple(translated)
                    )

            translated = [f"{tag}:{default_lang}" for tag in osm_keys]
            self.mapping[field] = (
                (translated[0], osm_keys[0]) if is_str else tuple(translated + osm_keys)
            )

    def get_osm_id(self):
        if self.object.provider.name.startswith("OpenStreetMap"):
            eid = self.object.eid
            osm_type = self.type_map.get(eid[0], None)
            osm_id = eid[1:]

            return osm_type, osm_id
        else:
            msg = _("The object does not have OpenStreetMap provider")
            raise Exception(msg)

    def map_fields(self, geotrek, osm):
        osm_keys = osm.get("tags", {})
        context = [
            {
                "geotrek_field": "eid",
                "geotrek_value": geotrek.eid,
                "osm_field": "ID",
                "osm_value": f"{osm.get('type')}({osm.get('id')})",
            }
        ]

        for geotrek_field, osm_fields in sorted(self.mapping.items()):
            fields = (osm_fields,) if isinstance(osm_fields, str) else osm_fields
            osm_value, osm_field = next(
                ((value, field) for field in fields if (value := osm_keys.get(field))),
                ("", fields[0]),
            )

            context.append(
                {
                    "geotrek_field": geotrek_field,
                    "geotrek_value": getattr(geotrek, geotrek_field, ""),
                    "osm_field": osm_field,
                    "osm_value": osm_value,
                }
            )

        return context

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        # add translation fields
        self.translation()

        # get OpenStreetMap object
        try:
            osm_type, osm_id = self.get_osm_id()
            self.osm_object = get_element(osm_type, osm_id)
        except Exception as e:
            messages.error(request, str(e))

            app_name = self.model._meta.app_label.lower()
            model = self.model._meta.verbose_name.lower()
            pk = self.object.pk
            return redirect(f"{app_name}:{model}_detail", pk=pk)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        app_name = self.model._meta.app_label.lower()
        model = self.model._meta.verbose_name.lower()

        context = super().get_context_data(**kwargs)

        # create context
        objects = self.map_fields(self.object, self.osm_object)
        context.update(
            {
                "objects": objects,
                "osm_object_serialized": json.dumps(self.osm_object),
                "validation_url": f"{app_name}:{model}_osm_validate",
            }
        )

        # if geotrek object have values longer than 255 caracters display a warning message
        has_long_values = any(len(item["geotrek_value"]) > 255 for item in objects)
        if has_long_values:
            msg = _(
                "OpenStreetMap only accepts values up to 255 characters. Any values exceeding this limit will be truncated."
            )
            messages.warning(self.request, msg)

        return context


class OSMValidationViewMixin(FormView):
    """
    Mixin for form views that handles validation and submission of OpenStreetMap object updates.

    Processes field modifications from comparison view and submits changes to OpenStreetMap
    using the standard changeset workflow (create → update → close). Handles user authentication
    via OSM token and provides feedback through Django messages.

    Requires:
        - User with valid OSM token in UserProfile
        - OSM configuration (OSM_APPLICATION_NAME)
        - POST parameters: osm_object (serialized) and field updates as "tag|value"
    """

    form_class = OSMForm
    template_name = "common/osm_validation.html"

    def get_updated_osm_object(self):
        osm_object_serialized = self.request.POST.get("osm_object", "{}")
        osm_object = json.loads(osm_object_serialized)

        for key, value in self.request.GET.items():
            if key != "osm_object":
                try:
                    tag, val = value.split("|", 1)
                    osm_object["tags"][tag] = val or osm_object["tags"].get(tag)
                except ValueError:
                    continue

        return osm_object_serialized, osm_object

    def get_context_data(self, **kwargs):
        osm_object_serialized, osm_object = self.get_updated_osm_object()

        context = super().get_context_data(**kwargs)

        context.update(
            {"object": osm_object, "osm_object_serialized": osm_object_serialized}
        )
        return context

    def get_success_url(self):
        pk = self.kwargs["pk"]
        model_name = self.model._meta.verbose_name.lower()
        return f"/{model_name}/{pk}"

    def form_valid(self, form):
        user_id = self.request.user.id
        token = UserProfile.objects.get(user_id=user_id).osm_token
        user_agent = f"{settings.OSM_APPLICATION_NAME}/0.1"

        osm_object_serialized, osm_object = self.get_updated_osm_object()

        # create changeset
        try:
            comment = form.cleaned_data.get("comment", "")
            changeset_id = create_changeset(token, user_agent, comment)
        except requests.exceptions.RequestException as e:
            messages.error(self.request, e)
            return super().form_valid(form)

        # update object
        try:
            update_element(token, changeset_id, osm_object)
        except requests.exceptions.RequestException as e:
            messages.error(self.request, e)
            return super().form_valid(form)

        # close changeset
        try:
            close_changeset(token, changeset_id)
        except requests.exceptions.RequestException as e:
            messages.error(self.request, e)
            return super().form_valid(form)

        msg = _("Saved")
        messages.success(self.request, msg)
        return super().form_valid(form)
