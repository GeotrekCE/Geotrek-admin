from django.db import models
from django.utils.tree import Node
from modeltranslation.manager import MultilingualQuerySet, rewrite_lookup_key


def _rewrite_f(self, q):
    if isinstance(q, models.F):
        name = getattr(q, "name", None)
        if name is not None:
            q.name = rewrite_lookup_key(self.model, name)
        return q
    if isinstance(q, Node):
        q.children = [self._rewrite_f(child) for child in q.children]
        return q

    if hasattr(q, "get_source_expressions") and hasattr(q, "set_source_expressions"):
        q.set_source_expressions(
            [self._rewrite_f(expression) for expression in q.get_source_expressions()]
        )
        return q

    if hasattr(q, "lhs"):
        q.lhs = self._rewrite_f(q.lhs)
    if hasattr(q, "rhs"):
        q.rhs = self._rewrite_f(q.rhs)
    return q

# treebeard 5 updates tree paths with Django expressions that modeltranslation 0.20
# rewrites via mutable lhs/rhs attributes. Patching the queryset method at startup keeps
# translated tree models working until the upstream incompatibility is resolved.
if not getattr(MultilingualQuerySet, "_geotrek_treebeard_compat", False):
    MultilingualQuerySet._rewrite_f = _rewrite_f
    MultilingualQuerySet._geotrek_treebeard_compat = True
