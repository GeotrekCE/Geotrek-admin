import logging
from collections import defaultdict

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.contrib.gis.db.models.functions import Transform
from django.db.models import Prefetch, Sum
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic.detail import BaseDetailView
from mapentity.helpers import user_has_perm
from mapentity.serializers import GPXSerializer
from mapentity.views import (
    LastModifiedMixin,
    MapEntityCreate,
    MapEntityDelete,
    MapEntityDetail,
    MapEntityDocument,
    MapEntityFilter,
    MapEntityFormat,
    MapEntityList,
    MapEntityMultiDelete,
    MapEntityMultiUpdate,
    MapEntityUpdate,
)
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from geotrek.authent.decorators import same_structure_required
from geotrek.common.functions import Length
from geotrek.common.mixins.forms import FormsetMixin
from geotrek.common.mixins.views import BelongStructureMixin, CustomColumnsMixin
from geotrek.common.permissions import PublicOrReadPermMixin
from geotrek.common.viewsets import GeotrekMapentityViewSet

from .filters import PathFilterSet, TrailFilterSet
from .forms import CertificationTrailFormSet, PathForm, TrailForm
from .models import AltimetryMixin, CertificationTrail, Path, Topology, Trail
from .path_router import PathRouter
from .serializers import (
    PathGeojsonSerializer,
    PathSerializer,
    TrailGeojsonSerializer,
    TrailSerializer,
)
from .layers import PathVectorLayer

logger = logging.getLogger(__name__)


class CreateFromTopologyMixin:
    def on_topology(self):
        pk = self.request.GET.get("topology")
        if pk:
            try:
                return Topology.objects.existing().get(pk=pk)
            except Topology.DoesNotExist:
                logger.warning("Intervention on unknown topology %s", pk)
        return None

    def get_initial(self):
        initial = super().get_initial()
        # Create intervention with an existing topology as initial data
        topology = self.on_topology()
        if topology:
            initial["topology"] = topology.serialize(with_pk=False)
        return initial


class PathList(CustomColumnsMixin, MapEntityList):
    queryset = Path.objects.all()
    mandatory_columns = ["id", "name", "length"]
    default_extra_columns = ["length_2d"]
    searchable_columns = ["id", "name"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_add"] = user_has_perm(
            self.request.user, "core.add_path"
        ) or user_has_perm(self.request.user, "core.add_draft_path")
        context["can_edit"] = user_has_perm(
            self.request.user, "core.change_path"
        ) or user_has_perm(self.request.user, "core.change_draft_path")
        context["can_delete"] = user_has_perm(
            self.request.user, "core.delete_path"
        ) or user_has_perm(self.request.user, "core.delete_draft_path")
        return context


class PathFilter(MapEntityFilter):
    model = Path
    filterset_class = PathFilterSet


class PathFormatList(MapEntityFormat, PathList):
    filterset_class = PathFilterSet
    mandatory_columns = ["id"]
    default_extra_columns = [
        "structure",
        "valid",
        "visible",
        "name",
        "comments",
        "departure",
        "arrival",
        "comfort",
        "source",
        "stake",
        "usages",
        "networks",
        "date_insert",
        "date_update",
        "length_2d",
        "uuid",
        *AltimetryMixin.COLUMNS,
    ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("structure", "comfort", "source", "stake")
            .prefetch_related("usages", "networks")
        )


class PathDetail(MapEntityDetail):
    model = Path

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["can_edit"] = self.get_object().same_structure(self.request.user)
        return context


class PathGPXDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = Path.objects.all()

    def render_to_response(self, context):
        gpx_serializer = GPXSerializer()
        response = HttpResponse(content_type="application/gpx+xml")
        response["Content-Disposition"] = f'attachment; filename="{self.object}.gpx"'
        gpx_serializer.serialize([self.object], stream=response, gpx_field="geom_3d")
        return response


class PathKMLDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = Path.objects.all()

    def render_to_response(self, context):
        response = HttpResponse(
            self.object.kml(), content_type="application/vnd.google-earth.kml+xml"
        )
        response["Content-Disposition"] = f'attachment; filename="{self.object}.kml"'
        return response


class PathDocument(MapEntityDocument):
    model = Path

    def get_context_data(self, *args, **kwargs):
        language = self.request.LANGUAGE_CODE
        self.get_object().prepare_elevation_chart(language)
        return super().get_context_data(*args, **kwargs)


class PathCreate(MapEntityCreate):
    model = Path
    form_class = PathForm

    def dispatch(self, *args, **kwargs):
        if self.request.user.has_perm("core.add_path") or self.request.user.has_perm(
            "core.add_draft_path"
        ):
            return super(MapEntityCreate, self).dispatch(*args, **kwargs)
        return super().dispatch(*args, **kwargs)


class PathUpdate(MapEntityUpdate):
    model = Path
    form_class = PathForm

    @same_structure_required("core:path_detail")
    def dispatch(self, *args, **kwargs):
        path = self.get_object()
        if path.draft and not self.request.user.has_perm("core.change_draft_path"):
            messages.warning(
                self.request,
                _(
                    "Access to the requested resource is restricted. You have been redirected."
                ),
            )
            return redirect("core:path_detail", **kwargs)
        if not path.draft and not self.request.user.has_perm("core.change_path"):
            messages.warning(
                self.request,
                _(
                    "Access to the requested resource is restricted. You have been redirected."
                ),
            )
            return redirect("core:path_detail", **kwargs)
        if path.draft and self.request.user.has_perm("core.change_draft_path"):
            return super(MapEntityUpdate, self).dispatch(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        path = self.get_object()
        if path.draft and self.request.user.has_perm("core.delete_draft_path"):
            kwargs["can_delete"] = True
        return kwargs


class PathDelete(MapEntityDelete):
    model = Path

    @same_structure_required("core:path_detail")
    def dispatch(self, *args, **kwargs):
        path = self.get_object()
        if path.draft and not self.request.user.has_perm("core.delete_draft_path"):
            messages.warning(
                self.request,
                _(
                    "Access to the requested resource is restricted. You have been redirected."
                ),
            )
            return redirect("core:path_detail", **kwargs)
        if not path.draft and not self.request.user.has_perm("core.delete_path"):
            messages.warning(
                self.request,
                _(
                    "Access to the requested resource is restricted. You have been redirected."
                ),
            )
            return redirect("core:path_detail", **kwargs)
        if path.draft and self.request.user.has_perm("core.delete_draft_path"):
            return super(MapEntityDelete, self).dispatch(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        topologies_by_model = defaultdict(list)
        self.object.topologies_by_path(topologies_by_model)
        context["topologies_by_model"] = dict(topologies_by_model)
        return context


class PathViewSet(GeotrekMapentityViewSet):
    model = Path
    serializer_class = PathSerializer
    geojson_serializer_class = PathGeojsonSerializer
    filterset_class = PathFilterSet
    mapentity_list_class = PathList
    layer_mapping = [PathVectorLayer]

    def get_permissions(self):
        if self.action == "route_geometry":
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def view_cache_key(self):
        """Used by the ``view_cache_response_content`` decorator."""
        return "no_draft" if self.request.GET.get("_no_draft") else "with_draft"

    def get_queryset(self):
        qs = self.model.objects.all()
        if self.format_kwarg == "geojson":
            if self.request.GET.get("_no_draft"):
                qs = qs.exclude(draft=True)
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "name", "draft")
        else:
            qs = qs.defer("geom", "geom_cadastre", "geom_3d")
        return qs

    def get_filter_count_infos(self, qs):
        """Add total path length to count infos in List dropdown menu"""
        data = super().get_filter_count_infos(qs)
        return f"{data} ({round(qs.aggregate(sumPath=Sum(Length('geom') / 1000)).get('sumPath') or 0, 1)} km)"

    @method_decorator(permission_required("core.change_path"))
    @action(methods=["POST"], detail=False, renderer_classes=[JSONRenderer])
    def merge_path(self, request, *args, **kwargs):
        try:
            ids_path_merge = request.POST.getlist("path[]")

            if len(ids_path_merge) != 2:
                raise Exception(_("You should select two paths"))
            paths = [int(path) for path in ids_path_merge]
            path_a = Path.objects.get(pk=min(paths))
            path_b = Path.objects.get(pk=max(paths))

            if not path_a.same_structure(request.user) or not path_b.same_structure(
                request.user
            ):
                raise Exception(_("You don't have the right to change these paths"))

            if path_a.draft != path_b.draft:
                raise Exception(_("You can't merge 1 draft path with 1 normal path"))

            result = path_a.merge_path(path_b)

            if result == 2:
                raise Exception(
                    _("You can't merge 2 paths with a 3rd path in the intersection")
                )

            elif result == 0:
                raise Exception(_("No matching points to merge paths found"))

            else:
                response = {"success": _("Paths merged successfully")}
                messages.success(request, response["success"])

        except Exception as exc:
            response = {
                "error": f"{exc}",
            }

        return Response(response)

    @action(
        methods=["POST"],
        detail=False,
        url_path="route-geometry",
        renderer_classes=[JSONRenderer],
    )
    def route_geometry(self, request, *args, **kwargs):
        try:
            params = request.data
            steps = params.get("steps")
            if steps is None:
                msg = "Request parameters should contain a 'steps' array"
                raise Exception(msg)
            if len(steps) < 2:
                msg = "There must be at least 2 steps"
                raise Exception(msg)
            for step in steps:
                position_on_path = step.get("positionOnPath")
                if (
                    not isinstance(position_on_path, int | float)
                    or position_on_path < 0
                    or position_on_path > 1
                ):
                    msg = "Each step should contain a valid position on its associated path (between 0 and 1)"
                    raise Exception(msg)
                path_id = step.get("path_id")
                if (
                    not isinstance(path_id, int)
                    or Path.objects.filter(pk=path_id).first() is None
                ):
                    msg = "Each step should contain a valid path id"
                    raise Exception(msg)
        except Exception as exc:
            return Response(
                {
                    "error": f"{exc}",
                },
                400,
            )

        try:
            path_router = PathRouter()
            response = path_router.get_route(steps)
            if response is not None:
                status = 200
            else:
                response = {"error": "No path between the given points"}
                status = 400
        except Exception as exc:
            response, status = (
                {
                    "error": f"{exc}",
                },
                500,
            )
        return Response(response, status)


class PathMultiDelete(BelongStructureMixin, MapEntityMultiDelete):
    model = Path

    def get(self, request, *args, **kwargs):
        # check pks definition first to avoid get_queryset error
        response = super().get(request, *args, **kwargs)

        if isinstance(response, HttpResponseRedirect):
            return response

        # check permissions
        qs = self.get_queryset()

        has_drafts = qs.filter(draft=True).exists()
        has_non_drafts = qs.filter(draft=False).exists()

        if (
            has_drafts
            and not user_has_perm(self.request.user, "core.delete_draft_path")
        ) or (
            has_non_drafts and not user_has_perm(self.request.user, "core.delete_path")
        ):
            messages.warning(
                self.request,
                _(
                    "Access to the requested resource is restricted. You have been redirected."
                ),
            )
            return redirect("core:path_list")

        return response


class PathMultiUpdate(BelongStructureMixin, MapEntityMultiUpdate):
    model = Path

    def get(self, request, *args, **kwargs):
        # check pks definition first to avoid get_queryset error
        response = super().get(request, *args, **kwargs)

        if isinstance(response, HttpResponseRedirect):
            return response

        # check permissions
        qs = self.get_queryset()

        has_drafts = qs.filter(draft=True).exists()
        has_non_drafts = qs.filter(draft=False).exists()

        if (
            has_drafts
            and not user_has_perm(self.request.user, "core.change_draft_path")
        ) or (
            has_non_drafts and not user_has_perm(self.request.user, "core.change_path")
        ):
            messages.warning(
                self.request,
                _(
                    "Access to the requested resource is restricted. You have been redirected."
                ),
            )
            return redirect("core:path_list")

        return response


class CertificationTrailMixin(FormsetMixin):
    context_name = "certificationtrail_formset"
    formset_class = CertificationTrailFormSet


class TrailList(CustomColumnsMixin, MapEntityList):
    queryset = Trail.objects.existing()
    mandatory_columns = ["id", "name"]
    default_extra_columns = ["departure", "arrival", "length"]
    searchable_columns = [
        "id",
        "name",
        "departure",
        "arrival",
    ]


class TrailFilter(MapEntityFilter):
    model = Trail
    filterset_class = TrailFilterSet


class TrailFormatList(MapEntityFormat, TrailList):
    filterset_class = TrailFilterSet
    mandatory_columns = ["id"]
    default_extra_columns = [
        "structure",
        "name",
        "comments",
        "departure",
        "arrival",
        "category",
        "certifications",
        "date_insert",
        "date_update",
        "cities",
        "districts",
        "areas",
        "uuid",
        *AltimetryMixin.COLUMNS,
    ]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("category__structure")
            .prefetch_related(
                Prefetch(
                    "certifications",
                    queryset=CertificationTrail.objects.select_related(
                        "certification_label", "certification_status"
                    ),
                )
            )
        )


class TrailDetail(MapEntityDetail):
    queryset = Trail.objects.existing()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["can_edit"] = self.get_object().same_structure(self.request.user)
        return context


class TrailGPXDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = Trail.objects.existing()

    def render_to_response(self, context):
        gpx_serializer = GPXSerializer()
        response = HttpResponse(content_type="application/gpx+xml")
        response["Content-Disposition"] = f'attachment; filename="{self.object}.gpx"'
        gpx_serializer.serialize([self.object], stream=response, gpx_field="geom_3d")
        return response


class TrailKMLDetail(LastModifiedMixin, PublicOrReadPermMixin, BaseDetailView):
    queryset = Trail.objects.existing()

    def render_to_response(self, context):
        response = HttpResponse(
            self.object.kml(), content_type="application/vnd.google-earth.kml+xml"
        )
        response["Content-Disposition"] = f'attachment; filename="{self.object}.kml"'
        return response


class TrailDocument(MapEntityDocument):
    queryset = Trail.objects.existing()


class TrailCreate(CreateFromTopologyMixin, CertificationTrailMixin, MapEntityCreate):
    model = Trail
    form_class = TrailForm


class TrailUpdate(CertificationTrailMixin, MapEntityUpdate):
    queryset = Trail.objects.existing()
    form_class = TrailForm

    @same_structure_required("core:trail_detail")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TrailDelete(MapEntityDelete):
    queryset = Trail.objects.existing()

    @same_structure_required("core:trail_detail")
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class TrailViewSet(GeotrekMapentityViewSet):
    model = Trail
    serializer_class = TrailSerializer
    geojson_serializer_class = TrailGeojsonSerializer
    filterset_class = TrailFilterSet
    mapentity_list_class = TrailList

    def get_queryset(self):
        qs = self.model.objects.existing()
        if self.format_kwarg == "geojson":
            qs = qs.annotate(api_geom=Transform("geom", settings.API_SRID))
            qs = qs.only("id", "name")
        else:
            qs = qs.defer("geom", "geom_3d")
        return qs


class TrailMultiDelete(BelongStructureMixin, MapEntityMultiDelete):
    model = Trail


class TrailMultiUpdate(BelongStructureMixin, MapEntityMultiUpdate):
    model = Trail
