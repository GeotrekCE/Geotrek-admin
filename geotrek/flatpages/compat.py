from django.db import models
from django.utils.tree import Node
from modeltranslation.manager import MultilingualQuerySet, rewrite_lookup_key


def _rewrite_f(self, q):
    if isinstance(q, models.F):
        q.name = rewrite_lookup_key(self.model, q.name)
        return q
    if isinstance(q, Node):
        q.children = list(map(self._rewrite_f, q.children))
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


if not getattr(MultilingualQuerySet, "_geotrek_treebeard_compat", False):
    MultilingualQuerySet._rewrite_f = _rewrite_f
    MultilingualQuerySet._geotrek_treebeard_compat = True
