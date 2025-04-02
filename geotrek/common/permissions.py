from django.core.exceptions import PermissionDenied
from mapentity.models import MapEntityRestPermissions


class PublicOrReadPermMixin:
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if not obj.is_public():
            if not self.request.user.is_authenticated:
                raise PermissionDenied
            if not self.request.user.has_perm(
                "%s.read_%s" % (obj._meta.app_label, obj._meta.model_name)
            ):
                raise PermissionDenied
        return obj


class RelatedPublishedPermission(MapEntityRestPermissions):
    def has_object_permission(self, request, view, obj):
        # This object is public if related object is published
        # If unpublished, only logged in users can access it, if they have view rights
        return super().has_permission(request, view) or obj.content_object.any_published

    def has_permission(self, request, view):
        # Permissions are defined at object level here
        return True
