from django.contrib.gis.db import models
from django.db.models import Manager
from treebeard.mp_tree import MP_NodeManager, MP_NodeQuerySet


class SiteQuerySet(MP_NodeQuerySet):
    def get_ancestors(self, include_self=False):
        paths = self.values_list("path", flat=True)
        ancestor_paths = set()
        steplen = self.model.steplen
        for path in paths:
            if not path:
                continue
            end = len(path) if include_self else len(path) - steplen
            for pos in range(steplen, end + 1, steplen):
                ancestor_paths.add(path[:pos])
        if not ancestor_paths:
            return self.none()
        return self.model.objects.filter(path__in=ancestor_paths)


class SiteManager(MP_NodeManager):
    def get_queryset(self):
        return SiteQuerySet(self.model, using=self._db).order_by("path")


class CourseOrderedChildManager(models.Manager):
    use_for_related_fields = True

    def get_queryset(self):
        # Select treks foreign keys by default
        return super().get_queryset().select_related("parent", "child")


class CourseManager(Manager):
    pass
