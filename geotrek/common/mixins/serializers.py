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

    def _check_assigned_structure(self, validated_data):
        user = self.context["request"].user
        if not (user.is_superuser or user.has_perm("authent.can_bypass_structure")):
            validated_data["structure"] = user.profile.structure

        return validated_data
