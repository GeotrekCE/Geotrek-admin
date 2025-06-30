import requests
import json

import xml.etree.ElementTree as ET

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.gis.db.models.functions import Transform
from django.db.models.query import Prefetch
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import translation
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.utils.translation import gettext as _
from django.views.generic import CreateView, DetailView, FormView
from django.views.generic.detail import BaseDetailView
from mapentity.helpers import alphabet_enumeration
from mapentity.views import (
    LastModifiedMixin,
    MapEntityCreate,
    MapEntityDelete,
    MapEntityDetail,
    MapEntityDocument,
    MapEntityFilter,
    MapEntityFormat,
    MapEntityList,
    MapEntityMapImage,
    MapEntityUpdate,
)
from rest_framework import permissions as rest_permissions
from rest_framework import viewsets

from geotrek.authent.decorators import same_structure_required
from geotrek.common.forms import AttachmentAccessibilityForm, OSMForm
from geotrek.common.mixins.views import CompletenessMixin, CustomColumnsMixin
from geotrek.common.models import (
    Attachment,
    HDViewPoint,
    Label,
    RecordSource,
    TargetPortal,
)
from geotrek.common.permissions import PublicOrReadPermMixin
from geotrek.common.views import DocumentBookletPublic, DocumentPublic, MarkupPublic
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.common.utils.translation import get_translated_fields
from geotrek.core.models import AltimetryMixin
from geotrek.core.views import CreateFromTopologyMixin
from geotrek.infrastructure.models import Infrastructure
from geotrek.infrastructure.serializers import InfrastructureAPIGeojsonSerializer
from geotrek.signage.models import Signage
from geotrek.signage.serializers import SignageAPIGeojsonSerializer
from geotrek.zoning.models import City, District, RestrictedArea

from .filters import POIFilterSet, ServiceFilterSet, TrekFilterSet
from .forms import POIForm, ServiceForm, TrekForm, WebLinkCreateFormPopup
from .models import POI, Service, Trek, WebLink
from .serializers import (
    POIGeojsonSerializer,
    POISerializer,
    ServiceGeojsonSerializer,
    ServiceSerializer,
    TrekGeojsonSerializer,
    TrekGPXSerializer,
    TrekPOIAPIGeojsonSerializer,
    TrekSerializer,
    TrekServiceAPIGeojsonSerializer,
)


class FlattenPicturesMixin:
    def get_queryset(self):
        """Override queryset to avoid attachment lookup while serializing.
        It will fetch attachments, and force ``pictures`` attribute of instances.
        """
        qs = super().get_queryset()
        qs.prefetch_related(
            Prefetch(
                "attachments",
                queryset=Attachment.objects.filter(is_image=True)
                .exclude(title="mapimage")
                .order_by("-starred", "attachment_file"),
                to_attr="_pictures",
            )
        )
        return qs


class TrekList(CustomColumnsMixin, FlattenPicturesMixin, MapEntityList):
    queryset = Trek.objects.existing()
    mandatory_columns = ["id", "name"]
    default_extra_columns = ["duration", "difficulty", "departure", "thumbnail"]
    unorderable_columns = ["thumbnail"]
    searchable_columns = ["id", "name", "departure", "arrival"]


class TrekFilter(MapEntityFilter):
    model = Trek
    filterset_class = TrekFilterSet


class TrekFormatList(MapEntityFormat, TrekList):
    filterset_class = TrekFilterSet
    mandatory_columns = ["id", "name"]
    default_extra_columns = [
        "eid",
        "eid2",
        "structure",
        "departure",
        "arrival",
        "duration",
        "duration_pretty",
        "description",
        "description_teaser",
        "networks",
        "advice",
        "gear",
        "ambiance",
        "difficulty",
        "information_desks",
        "themes",
        "practice",
        "ratings",
        "ratings_description",
        "accessibilities",
        "accessibility_advice",
        "accessibility_covering",
        "accessibility_exposure",
        "accessibility_level",
        "accessibility_signage",
        "accessibility_slope",
        "accessibility_width",
        "accessibility_infrastructure",
        "access",
        "route",
        "public_transport",
        "advised_parking",
        "web_links",
        "labels",
        "parking_location",
        "points_reference",
        "children",
        "parents",
        "pois",
        "review",
        "published",
        "publication_date",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "source",
        "portal",
        "length_2d",
        "uuid",
        *AltimetryMixin.COLUMNS,
    ]


class TrekGPXDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        gpx_serializer = TrekGPXSerializer()
        response = HttpResponse(content_type="application/gpx+xml")
        response["Content-Disposition"] = (
            f"attachment; filename={self.get_object().slug}.gpx"
        )
        gpx_serializer.serialize(
            [self.get_object()], stream=response, gpx_field="geom_3d"
        )
        return response


class TrekKMLDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = Trek.objects.existing()

    def render_to_response(self, context):
        trek = self.get_object()
        response = HttpResponse(
            trek.kml(), content_type="application/vnd.google-earth.kml+xml"
        )
        return response


class TrekDetail(CompletenessMixin, MapEntityDetail):
    queryset = (
        Trek.objects.existing()
        .select_related("topo_object", "structure")
        .prefetch_related(
            Prefetch(
                "view_points",
                queryset=HDViewPoint.objects.select_related("content_type", "license"),
            )
        )
    )

    @property
    def icon_sizes(self):
        return {
            "POI": settings.TREK_ICON_SIZE_POI,
            "service": settings.TREK_ICON_SIZE_SERVICE,
            "signage": settings.TREK_ICON_SIZE_SIGNAGE,
            "infrastructure": settings.TREK_ICON_SIZE_INFRASTRUCTURE,
            "parking": settings.TREK_ICON_SIZE_PARKING,
            "information_desk": settings.TREK_ICON_SIZE_INFORMATION_DESK,
        }

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["can_edit"] = self.get_object().same_structure(self.request.user)
        context["labels"] = Label.objects.all()
        context["accessibility_form"] = AttachmentAccessibilityForm(
            request=self.request, object=self.get_object()
        )
        return context


class TrekMapImage(MapEntityMapImage):
    queryset = Trek.objects.existing()


class TrekDocument(MapEntityDocument):
    queryset = Trek.objects.existing()


class TrekDocumentPublicMixin:
    queryset = Trek.objects.existing()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trek = self.get_object()

        context["headerimage_ratio"] = settings.EXPORT_HEADER_IMAGE_SIZE["trek"]

        information_desks = list(trek.information_desks.all())
        if settings.TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT > 0:
            information_desks = information_desks[
                : settings.TREK_EXPORT_INFORMATION_DESK_LIST_LIMIT
            ]

        context["information_desks"] = information_desks
        pois = list(trek.published_pois.all())
        if settings.TREK_EXPORT_POI_LIST_LIMIT > 0:
            pois = pois[: settings.TREK_EXPORT_POI_LIST_LIMIT]
        letters = alphabet_enumeration(len(pois))
        for i, poi in enumerate(pois):
            poi.letter = letters[i]
        context["pois"] = pois
        infrastructures = list(trek.published_infrastructures.all())
        signages = list(trek.published_signages.all())
        context["infrastructures"] = infrastructures
        context["signages"] = signages
        context["object"] = context["trek"] = trek
        source = self.request.GET.get("source")
        if source:
            try:
                context["source"] = RecordSource.objects.get(name=source)
            except RecordSource.DoesNotExist:
                pass
        portal = self.request.GET.get("portal")
        if portal:
            try:
                context["portal"] = TargetPortal.objects.get(name=portal)
            except TargetPortal.DoesNotExist:
                pass
        return context

    def render_to_response(self, context, **response_kwargs):
        # Prepare altimetric graph
        trek = self.get_object()
        language = self.request.LANGUAGE_CODE
        trek.prepare_elevation_chart(language)
        return super().render_to_response(context, **response_kwargs)


class TrekDocumentPublic(TrekDocumentPublicMixin, DocumentPublic):
    pass


class TrekDocumentBookletPublic(TrekDocumentPublicMixin, DocumentBookletPublic):
    pass


class TrekMarkupPublic(TrekDocumentPublicMixin, MarkupPublic):
    pass


class TrekCreate(CreateFromTopologyMixin, MapEntityCreate):
    model = Trek
    form_class = TrekForm


class TrekUpdate(MapEntityUpdate):
    queryset = Trek.objects.existing()
    form_class = TrekForm

    @same_structure_required("trekking:trek_detail")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TrekDelete(MapEntityDelete):
    model = Trek

    @same_structure_required("trekking:trek_detail")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TrekViewSet(GeotrekMapentityViewSet):
    model = Trek
    serializer_class = TrekSerializer
    geojson_serializer_class = TrekGeojsonSerializer
    filterset_class = TrekFilterSet
    mapentity_list_class = TrekList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "name", "published")
        else:
            qs = qs.prefetch_related("attachments")
        return qs


class POIList(CustomColumnsMixin, FlattenPicturesMixin, MapEntityList):
    queryset = POI.objects.existing()
    mandatory_columns = ["id", "name"]
    default_extra_columns = ["type", "thumbnail"]
    unorderable_columns = ["thumbnail"]
    searchable_columns = [
        "id",
        "name",
    ]


class POIFilter(MapEntityFilter):
    model = POI
    filterset_class = POIFilterSet


class POIFormatList(MapEntityFormat, POIList):
    filterset_class = POIFilterSet
    mandatory_columns = ["id"]
    default_extra_columns = [
        "structure",
        "eid",
        "name",
        "type",
        "description",
        "treks",
        "review",
        "published",
        "publication_date",
        "structure",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "uuid",
        *AltimetryMixin.COLUMNS,
    ]

    def get_queryset(self):
        qs = super().get_queryset()

        denormalized = {}

        # Since Land layers should have less records, start by them.
        land_layers = [
            ("districts", District),
            ("cities", City),
            ("areas", RestrictedArea),
        ]
        for attrname, land_layer in land_layers:
            denormalized[attrname] = {}
            for d in land_layer.objects.all():
                overlapping = POI.objects.existing().filter(geom__within=d.geom)
                for pid in overlapping.values_list("id", flat=True):
                    denormalized[attrname].setdefault(pid, []).append(str(d))

        # Same for treks
        denormalized["treks"] = {}
        for d in Trek.objects.existing():
            for pid in d.pois.all():
                denormalized["treks"].setdefault(pid, []).append(d)
        for poi in qs:
            # Put denormalized in specific attribute used in serializers
            for attrname in denormalized.keys():
                overlapping = denormalized[attrname].get(poi.id, [])
                setattr(poi, f"{attrname}_csv_display", ", ".join(overlapping))
            yield poi


class POIDetail(CompletenessMixin, MapEntityDetail):
    queryset = (
        POI.objects.existing()
        .prefetch_related(
            Prefetch(
                "view_points",
                queryset=HDViewPoint.objects.select_related("content_type", "license"),
            )
        )
        .select_related("type")
    )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["can_edit"] = self.get_object().same_structure(self.request.user)
        return context


class POIDocument(MapEntityDocument):
    model = POI


class POICreate(MapEntityCreate):
    model = POI
    form_class = POIForm


class POIUpdate(MapEntityUpdate):
    queryset = POI.objects.existing()
    form_class = POIForm

    @same_structure_required("trekking:poi_detail")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class POIDelete(MapEntityDelete):
    model = POI

    @same_structure_required("trekking:poi_detail")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class WebLinkCreatePopup(CreateView):
    model = WebLink
    form_class = WebLinkCreateFormPopup

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponse(
            f"""
            <script type="text/javascript">opener.dismissAddAnotherPopup(window, "{escape(form.instance._get_pk_val())}", "{escape(form.instance)}");</script>
        """
        )


class POIViewSet(GeotrekMapentityViewSet):
    model = POI
    serializer_class = POISerializer
    geojson_serializer_class = POIGeojsonSerializer
    filterset_class = POIFilterSet
    mapentity_list_class = POIList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "name", "published")
        else:
            qs = qs.select_related("type", "structure")
            qs = qs.prefetch_related("attachments")
        return qs

class POIOSMCompare(DetailView):
    model = POI
    template_name = "trekking/poi_osm_comparaison.html"

    mapping = {
        "name": "name",
        "description": "description",
    }

    def translation(self):
        default_lang = settings.MODELTRANSLATION_DEFAULT_LANGUAGE

        for field in get_translated_fields(self.model):
            tags = self.mapping.get(field)
            if not tags:
                continue

            is_str = isinstance(tags, str)
            tags = [tags] if is_str else list(tags)

            # Protect the class from multiple translation mappings as field is a static attribute
            is_translated = [tag for tag in tags if tag.endswith(f":{default_lang}")]
            if is_translated:
                continue

            for lang in settings.MODELTRANSLATION_LANGUAGES:
                if lang != default_lang:
                    geotrek_field = f"{field}_{lang}"
                    translated = [tag + ":" + lang for tag in tags]
                    self.mapping[geotrek_field] = (
                        translated[0] if is_str else tuple(translated)
                    )

            translated = [f"{tag}:{default_lang}" for tag in tags]
            self.mapping[field] = (
                (translated[0], tags[0]) if is_str else tuple(translated + tags)
            )

    def get_osm_object(self, geotrek_object, **kwargs):
        eid = geotrek_object.eid

        type = "node" if eid[0] == "N" else \
               "way" if eid[0] == "W" else \
               "relation"
        id = eid[1:]

        response = requests.get(f"https://master.apis.dev.openstreetmap.org/api/0.6/{type}/{id}.json")
        if response.status_code == 404:
            raise Exception(f"OpenStreetMap object {type}({id}) not found")
        elif response.status_code == 410:
            raise Exception(f"OpenStreetMap object {type}({id}) has been deleted")

        return response.json()['elements'][0]

    def map_fields(self, geotrek, osm):
        osm_tags = osm.get("tags", {})
        context = [{
            "geotrek_field": "eid",
            "geotrek_value": geotrek.eid,
            "osm_field": "ID",
            "osm_value": f"{osm.get('type')}({osm.get('id')})"
        }]

        for geotrek_field, osm_fields in sorted(self.mapping.items()):
            fields = (osm_fields,) if isinstance(osm_fields, str) else osm_fields
            osm_value, osm_field = next(
                ((value, field) for field in fields if (value := osm_tags.get(field))),
                ("", fields[0])
            )

            context.append({
                "geotrek_field": geotrek_field,
                "geotrek_value": getattr(geotrek, geotrek_field, ""),
                "osm_field": osm_field,
                "osm_value": osm_value
            })

        return context

    def get_context_data(self, **kwargs):
        # add translation fields
        self.translation()

        # get geotrek object
        geotrek_object = self.model.objects.get(pk=self.kwargs["pk"])

        # get OpenStreetMap object
        osm_object = self.get_osm_object(geotrek_object)

        # create context
        context = super().get_context_data(**kwargs)
        context.update({
            "objects": self.map_fields(geotrek_object, osm_object),
            "osm_object_serialized": json.dumps(osm_object),
        })

        return context


class POIOSMValidate(FormView):
    template_name = "trekking/poi_osm_validation.html"
    form_class = OSMForm
    success_url = "/poi/list/"

    TOKEN = '4NnQ0aihS61B0lGqa2d6EdvRV9pt3MMVGbFVT53BVB8'
    USER_AGENT = 'Geotrek-admin/0.1'
    BASE_URL = 'https://master.apis.dev.openstreetmap.org/api/0.6'

    def get_updated_osm_object(self):
        # Récupération de l'objet OSM depuis les paramètres GET
        osm_object_serialized = self.request.GET.get("osm_object", "{}")
        osm_object = json.loads(osm_object_serialized)

        # Mise à jour des tags avec les valeurs GET supplémentaires
        for key, value in self.request.GET.items():
            if key != "osm_object":
                try:
                    tag, val = value.split("|", 1)
                    osm_object["tags"][tag] = val or osm_object["tags"].get(tag)
                except ValueError:
                    continue  # Ignore les valeurs mal formées

        return osm_object_serialized, osm_object

    def get_context_data(self, **kwargs):
        osm_object_serialized, osm_object = self.get_updated_osm_object()

        context = super().get_context_data(**kwargs)

        context.update({
            "object": osm_object,
            "osm_object_serialized": osm_object_serialized
        })
        return context

    def get_success_url(self):
        pk = self.kwargs["pk"]
        return f"/poi/{pk}"

    def form_valid(self, form):
        headers = {
            'Authorization': f'Bearer {self.TOKEN}',
            'User-Agent': self.USER_AGENT
        }

        xml_headers = headers.copy()
        xml_headers["Content-Type"] = "text/xml"

        osm_object_serialized, osm_object = self.get_updated_osm_object()

        # create changeset
        url = f"{self.BASE_URL}/changeset/create"

        changeset_osm = ET.Element("osm", {"version": "0.6"})
        changeset = ET.SubElement(changeset_osm, "changeset")
        ET.SubElement(changeset, "tag", k="created_by", v=self.USER_AGENT)
        ET.SubElement(changeset, "tag", k="comment", v=self.request.GET.get("comment", ""))

        changeset_xml = ET.tostring(changeset_osm, encoding='utf-8', xml_declaration=True).decode()

        response = requests.put(url,
                     headers=xml_headers,
                     data = changeset_xml)

        if response.status_code == 400:
            msg = _("Bad Request: Changeset")
            messages.error(self.request, msg)
            return super().form_valid(form)
        elif response.status_code == 405:
            msg = _("Method Not Allowed: Changeset")
            messages.error(self.request, msg)
            return super().form_valid(form)

        changeset_id = response.content.decode()

        # update object
        url = f"{self.BASE_URL}/{osm_object['type']}/{osm_object['id']}"

        element_osm = ET.Element("osm",  {"version": "0.6"})

        elements_tags = ["changeset", "id", "lat", "lon", "version", "visible"]

        attributs = {k: str(v) for k, v in osm_object.items() if k in elements_tags}
        attributs["changeset"] = changeset_id

        element = ET.SubElement(element_osm, osm_object["type"], attributs)

        if "nodes" in osm_object:
            for node in osm_object["nodes"]:
                ET.SubElement(element, "nd", {"ref": str(node)})

        if "members" in osm_object:
            for member in osm_object["members"]:
                ET.SubElement(element, "member", {
                    "type": str(member["type"]),
                    "ref": str(member["ref"]),
                    "role": str(member["role"]),
                })

        # tags
        for key, value in osm_object["tags"].items():
            ET.SubElement(element, "tag", {
                "k": key,
                "v": value
            })

        element_xml = ET.tostring(element_osm, encoding='utf-8', xml_declaration=True).decode()

        print("\n\n\n", element_xml, "\n\n\n")

        response = requests.put(url,
                                headers=xml_headers,
                                data=element_xml)

        if response.status_code == 400:
            msg = _("Bad Request: Element")
            messages.error(self.request, msg)
            return super().form_valid(form)
        elif response.status_code == 404:
            msg = _("Element not found")
            messages.error(self.request, msg)
            return super().form_valid(form)
        elif response.status_code == 409:
            msg = _("Changeset closed")
            messages.error(self.request, msg)
            return super().form_valid(form)
        elif response.status_code == 412:
            msg = _(f"Missing nodes/ways")
            messages.error(self.request, msg)
            return super().form_valid(form)
        elif response.status_code == 429:
            msg = _("Too Many Requests")
            messages.error(self.request, msg)
            return super().form_valid(form)

        # close changeset

        url = f"{self.BASE_URL}/changeset/{changeset_id}/close"

        response = requests.put(url,headers=headers)

        if response.status_code == 404:
            msg = _("Changeset not found")
            messages.error(self.request, msg)
            return super().form_valid(form)
        elif response.status_code == 405:
            msg = _("Method Not Allowed: Changeset")
            messages.error(self.request, msg)
            return super().form_valid(form)
        elif response.status_code == 409:
            msg = _("Changeset already closed")
            messages.error(self.request, msg)
            return super().form_valid(form)

        msg = _("Saved")
        messages.success(self.request, msg)
        return super().form_valid(form)


class TrekPOIViewSet(viewsets.ModelViewSet):
    model = POI
    serializer_class = TrekPOIAPIGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        pk = self.kwargs["pk"]
        trek = get_object_or_404(Trek.objects.existing(), pk=pk)
        if not self.request.user.has_perm("trekking.read_poi") and not trek.is_public():
            raise Http404
        return (
            trek.pois.filter(published=True)
            .annotate(api_geom=Transform("geom", settings.API_SRID))
            .select_related(
                "type",
            )
        )


class TrekSignageViewSet(viewsets.ModelViewSet):
    model = Signage
    serializer_class = SignageAPIGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        pk = self.kwargs["pk"]
        trek = get_object_or_404(Trek.objects.existing(), pk=pk)
        if (
            not self.request.user.has_perm("trekking.read_signage")
            and not trek.is_public()
        ):
            raise Http404
        return trek.signages.filter(published=True).annotate(
            api_geom=Transform("geom", settings.API_SRID)
        )


class TrekInfrastructureViewSet(viewsets.ModelViewSet):
    model = Infrastructure
    serializer_class = InfrastructureAPIGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        pk = self.kwargs["pk"]
        trek = get_object_or_404(Trek.objects.existing(), pk=pk)
        if (
            not self.request.user.has_perm("infrastructure.read_infrastructure")
            and not trek.is_public()
        ):
            raise Http404
        return trek.infrastructures.filter(published=True).annotate(
            api_geom=Transform("geom", settings.API_SRID)
        )


class ServiceList(CustomColumnsMixin, MapEntityList):
    queryset = Service.objects.existing()
    mandatory_columns = ["id", "name"]
    default_extra_columns = []
    searchable_columns = ["id"]


class ServiceFilter(MapEntityFilter):
    model = Service
    filterset_class = ServiceFilterSet


class ServiceFormatList(MapEntityFormat, ServiceList):
    filterset_class = ServiceFilterSet
    mandatory_columns = ["id"]
    default_extra_columns = ["id", "eid", "type", "uuid", *AltimetryMixin.COLUMNS]


class ServiceDetail(MapEntityDetail):
    queryset = Service.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["can_edit"] = self.get_object().same_structure(self.request.user)
        return context


class ServiceCreate(MapEntityCreate):
    model = Service
    form_class = ServiceForm


class ServiceUpdate(MapEntityUpdate):
    queryset = Service.objects.existing()
    form_class = ServiceForm

    @same_structure_required("trekking:service_detail")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ServiceDelete(MapEntityDelete):
    model = Service

    @same_structure_required("trekking:service_detail")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class ServiceViewSet(GeotrekMapentityViewSet):
    model = Service
    serializer_class = ServiceSerializer
    geojson_serializer_class = ServiceGeojsonSerializer
    filterset_class = ServiceFilterSet
    mapentity_list_class = ServiceList

    def get_queryset(self):
        qs = self.model.objects.existing().select_related("type")
        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "type")
        return qs


class TrekServiceViewSet(viewsets.ModelViewSet):
    model = Service
    serializer_class = TrekServiceAPIGeojsonSerializer
    permission_classes = [rest_permissions.DjangoModelPermissionsOrAnonReadOnly]

    def get_queryset(self):
        pk = self.kwargs["pk"]
        trek = get_object_or_404(Trek.objects.existing(), pk=pk)
        if (
            not self.request.user.has_perm("trekking.read_service")
            and not trek.is_public()
        ):
            raise Http404
        return trek.services.filter(type__published=True).annotate(
            api_geom=Transform("geom", settings.API_SRID)
        )


# Translations for public PDF
translation.gettext_noop("Advices")
translation.gettext_noop("Gear")
translation.gettext_noop("All useful information")
translation.gettext_noop("Altimetric profile")
translation.gettext_noop("Attribution")
translation.gettext_noop("Geographical location")
translation.gettext_noop("Markings")
translation.gettext_noop("Max elevation")
translation.gettext_noop("Min elevation")
translation.gettext_noop("On your path...")
translation.gettext_noop("Powered by geotrek.fr")
translation.gettext_noop(
    "The national park is an unrestricted natural area but subjected to regulations which must be known by all visitors."
)
translation.gettext_noop("This hike is in the core of the national park")
translation.gettext_noop("Trek ascent")
translation.gettext_noop("Useful information")
