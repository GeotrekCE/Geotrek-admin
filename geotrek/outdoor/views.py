from django.conf import settings
from django.contrib.gis.db.models.functions import Transform
from django.db.models import Prefetch
from geotrek.common.models import HDViewPoint
from mapentity.helpers import alphabet_enumeration
from mapentity.views import (MapEntityList, MapEntityFilter, MapEntityDetail, MapEntityDocument, MapEntityCreate,
                             MapEntityUpdate, MapEntityDelete, MapEntityFormat)

from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.views import CompletenessMixin, CustomColumnsMixin
from geotrek.common.views import DocumentBookletPublic, DocumentPublic, MarkupPublic
from geotrek.common.viewsets import GeotrekMapentityViewSet
from .filters import SiteFilterSet, CourseFilterSet
from .forms import SiteForm, CourseForm
from .models import Site, Course
from .serializers import SiteSerializer, CourseSerializer, SiteGeojsonSerializer, CourseGeojsonSerializer


class SiteList(CustomColumnsMixin, MapEntityList):
    queryset = Site.objects.all()
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['super_practices', 'date_update']
    searchable_columns = ['id', 'name']


class SiteFilter(MapEntityFilter):
    model = Site
    filterset_class = SiteFilterSet


class SiteDetail(CompletenessMixin, MapEntityDetail):
    queryset = Site.objects.all().prefetch_related(
        Prefetch('view_points',
                 queryset=HDViewPoint.objects.select_related('content_type', 'license'))
    )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class SiteCreate(MapEntityCreate):
    model = Site
    form_class = SiteForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['site'] = self.request.GET.get('parent_sites')
        return kwargs


class SiteUpdate(MapEntityUpdate):
    queryset = Site.objects.all()
    form_class = SiteForm

    @same_structure_required('outdoor:site_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SiteDelete(MapEntityDelete):
    template_name = "outdoor/site_confirm_delete.html"
    model = Site

    @same_structure_required('outdoor:site_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    # Add support for browsers which only accept GET and POST for now.
    def post(self, request, *args, **kwargs):
        return self.delete(request, *args, **kwargs)


class SiteDocumentPublicMixin:
    queryset = Site.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['site']
        context['object'] = context['content'] = site
        pois = list(site.all_pois.filter(published=True))
        if settings.TREK_EXPORT_POI_LIST_LIMIT > 0:
            pois = pois[:settings.TREK_EXPORT_POI_LIST_LIMIT]
        letters = alphabet_enumeration(len(pois))
        for i, poi in enumerate(pois):
            poi.letter = letters[i]
        context['pois'] = pois
        return context


class SiteDocument(MapEntityDocument):
    queryset = Site.objects.all()


class SiteDocumentPublic(SiteDocumentPublicMixin, DocumentPublic):
    pass


class SiteDocumentBookletPublic(SiteDocumentPublicMixin, DocumentBookletPublic):
    pass


class SiteMarkupPublic(SiteDocumentPublicMixin, MarkupPublic):
    pass


class SiteFormatList(MapEntityFormat, SiteList):
    filterset_class = SiteFilterSet
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'name', 'practice', 'description',
        'description_teaser', 'ambiance', 'advice', 'period', 'labels', 'themes',
        'portal', 'source', 'information_desks', 'web_links', 'accessibility', 'eid',
        'orientation', 'wind', 'ratings', 'managers', 'uuid',
    ]


class SiteViewSet(GeotrekMapentityViewSet):
    model = Site
    serializer_class = SiteSerializer
    geojson_serializer_class = SiteGeojsonSerializer
    filterset_class = SiteFilterSet
    mapentity_list_class = SiteList

    def get_queryset(self):
        qs = self.model.objects.all()
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'name')
        return qs


class CourseList(CustomColumnsMixin, MapEntityList):
    queryset = Course.objects.select_related('type').prefetch_related('parent_sites').all()
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['parent_sites', 'date_update']
    searchable_columns = ['id', 'name']


class CourseFilter(MapEntityFilter):
    model = Course
    filterset_class = CourseFilterSet


class CourseDetail(CompletenessMixin, MapEntityDetail):
    queryset = Course.objects.prefetch_related('type').all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class CourseCreate(MapEntityCreate):
    model = Course
    form_class = CourseForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['parent_sites'] = self.request.GET.get('parent_sites')
        return kwargs


class CourseUpdate(MapEntityUpdate):
    queryset = Course.objects.all()
    form_class = CourseForm

    @same_structure_required('outdoor:course_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CourseDelete(MapEntityDelete):
    model = Course

    @same_structure_required('outdoor:course_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class CourseDocumentPublicMixin:
    queryset = Course.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['course']
        context['object'] = context['content'] = course
        pois = list(course.all_pois.filter(published=True))
        if settings.TREK_EXPORT_POI_LIST_LIMIT > 0:
            pois = pois[:settings.TREK_EXPORT_POI_LIST_LIMIT]
        letters = alphabet_enumeration(len(pois))
        for i, poi in enumerate(pois):
            poi.letter = letters[i]
        context['pois'] = pois
        return context


class CourseDocument(MapEntityDocument):
    queryset = Course.objects.all()


class CourseDocumentPublic(CourseDocumentPublicMixin, DocumentPublic):
    pass


class CourseDocumentBookletPublic(CourseDocumentPublicMixin, DocumentBookletPublic):
    pass


class CourseMarkupPublic(CourseDocumentPublicMixin, MarkupPublic):
    pass


class CourseFormatList(MapEntityFormat, CourseList):
    filterset_class = CourseFilterSet
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'name', 'parent_sites', 'description', 'advice', 'equipment', 'accessibility',
        'eid', 'height', 'ratings', 'ratings_description', 'points_reference', 'uuid',
    ]


class CourseViewSet(GeotrekMapentityViewSet):
    model = Course
    serializer_class = CourseSerializer
    geojson_serializer_class = CourseGeojsonSerializer
    filterset_class = CourseFilterSet
    mapentity_list_class = CourseList

    def get_queryset(self):
        qs = self.model.objects.all()
        if self.format_kwarg == 'geojson':
            qs = qs.annotate(api_geom=Transform('geom', settings.API_SRID))
            qs = qs.only('id', 'name')
        else:
            qs = qs.prefetch_related('parent_sites')
        return qs
