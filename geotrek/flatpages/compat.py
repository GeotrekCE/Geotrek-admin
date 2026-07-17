from copy import copy
from threading import Lock

from django.db import models
from django.utils.tree import Node
from modeltranslation.manager import MultilingualQuerySet, rewrite_lookup_key

_PATCH_LOCK = Lock()


def _rewrite_f(self, q):
    if isinstance(q, models.F):
        name = getattr(q, "name", None)
        if name is not None:
            return models.F(rewrite_lookup_key(self.model, name))
        return q
    if isinstance(q, Node):
        rewritten = copy(q)
        rewritten.children = [self._rewrite_f(child) for child in q.children]
        return rewritten

    if hasattr(q, "get_source_expressions") and hasattr(q, "set_source_expressions"):
        rewritten = copy(q)
        rewritten.set_source_expressions(
            [self._rewrite_f(expression) for expression in q.get_source_expressions()]
        )
        return rewritten

    rewritten = copy(q)
    if hasattr(q, "lhs"):
        rewritten.lhs = self._rewrite_f(q.lhs)
    if hasattr(q, "rhs"):
        rewritten.rhs = self._rewrite_f(q.rhs)
    return rewritten

# treebeard 5 updates tree paths with Django expressions that modeltranslation 0.20
# rewrites via mutable lhs/rhs attributes. Patching the queryset method at startup keeps
# translated tree models working until the upstream incompatibility is resolved.
with _PATCH_LOCK:
    if not getattr(MultilingualQuerySet, "_geotrek_treebeard_compat", False):
        MultilingualQuerySet._rewrite_f = _rewrite_f
        MultilingualQuerySet._geotrek_treebeard_compat = True
