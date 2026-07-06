from django.db.models import Q


class LimitStructurePermission:
    def _apply_structure_limitation(self, fields, limited_fields, structure):
        for attribute, model, many in limited_fields:
            if many:
                fields[attribute].child_relation.queryset = model.objects.filter(
                    Q(structure=structure) | Q(structure__isnull=True)
                )
            else:
                fields[attribute].queryset = model.objects.filter(
                    Q(structure=structure) | Q(structure__isnull=True)
                )
