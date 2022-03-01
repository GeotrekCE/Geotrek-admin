from django.conf import settings
from mapentity.views import (MapEntityLayer, MapEntityList, MapEntityDetail, MapEntityCreate, MapEntityUpdate,
                             MapEntityDelete, MapEntityFormat)

from geotrek.authent.decorators import same_structure_required
from geotrek.common.mixins.views import CustomColumnsMixin
from geotrek.common.views import DocumentPublic, MarkupPublic
from geotrek.common.viewsets import GeotrekMapentityViewSet
from geotrek.outdoor.filters import SiteFilterSet, CourseFilterSet
from geotrek.outdoor.forms import SiteForm, CourseForm
from geotrek.outdoor.models import Site, Course
from geotrek.outdoor.serializers import SiteSerializer, CourseSerializer


class SiteLayer(MapEntityLayer):
    properties = ['name']
    filterform = SiteFilterSet
    queryset = Site.objects.all()


class SiteList(CustomColumnsMixin, MapEntityList):
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['super_practices', 'date_update']
    filterform = SiteFilterSet
    queryset = Site.objects.all()


class SiteDetail(MapEntityDetail):
    queryset = Site.objects.all()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['can_edit'] = self.get_object().same_structure(self.request.user)
        return context


class SiteCreate(MapEntityCreate):
    model = Site
    form_class = SiteForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['site'] = self.request.GET.get('site')
        return kwargs


class SiteUpdate(MapEntityUpdate):
    queryset = Site.objects.all()
    form_class = SiteForm

    @same_structure_required('outdoor:site_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SiteDelete(MapEntityDelete):
    model = Site

    @same_structure_required('outdoor:site_detail')
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class SiteDocumentPublicMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['site']
        context['object'] = context['content'] = content

        return context


class SiteDocumentPublic(SiteDocumentPublicMixin, DocumentPublic):
    pass


class SiteMarkupPublic(SiteDocumentPublicMixin, MarkupPublic):
    pass


class SiteFormatList(MapEntityFormat, SiteList):
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
    filterset_class = SiteFilterSet

    def get_columns(self):
        return SiteList.mandatory_columns + settings.COLUMNS_LISTS.get('site_view',
                                                                       SiteList.default_extra_columns)

    def get_queryset(self):
        return self.model.objects.all()


class CourseLayer(MapEntityLayer):
    properties = ['name']
    filterform = CourseFilterSet
    queryset = Course.objects.prefetch_related('type').all()


class CourseList(CustomColumnsMixin, MapEntityList):
    mandatory_columns = ['id', 'name']
    default_extra_columns = ['parent_sites', 'date_update']
    filterform = CourseFilterSet
    queryset = Course.objects.select_related('type').prefetch_related('parent_sites').all()


class CourseDetail(MapEntityDetail):
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
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        content = self.get_object()

        context['headerimage_ratio'] = settings.EXPORT_HEADER_IMAGE_SIZE['course']
        context['object'] = context['content'] = content

        return context


class CourseDocumentPublic(CourseDocumentPublicMixin, DocumentPublic):
    pass


class CourseMarkupPublic(CourseDocumentPublicMixin, MarkupPublic):
    pass


class CourseFormatList(MapEntityFormat, CourseList):
    mandatory_columns = ['id']
    default_extra_columns = [
        'structure', 'name', 'parent_sites', 'description', 'advice', 'equipment', 'accessibility',
        'eid', 'height', 'ratings', 'ratings_description', 'points_reference', 'uuid',
    ]


class CourseViewSet(GeotrekMapentityViewSet):
    model = Course
    serializer_class = CourseSerializer
    filterset_class = CourseFilterSet

    def get_columns(self):
        return CourseList.mandatory_columns + settings.COLUMNS_LISTS.get('course_view',
                                                                         CourseList.default_extra_columns)

    def get_queryset(self):
        return self.model.objects.all().prefetch_related('sites')
