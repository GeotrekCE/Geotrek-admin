from django.conf import settings
from django.db import migrations
from django.db.models.fields.related import ForeignKey


def fix_default_structure(apps, schema_editor):
    StructureModel = apps.get_model('authent', 'Structure')
    structure_pk = StructureModel.objects.get_or_create(name=settings.DEFAULT_STRUCTURE_NAME)[0].pk
    fields = StructureModel._meta.get_fields()
    StructureModel.objects.filter(id=structure_pk).update(id=1)
    for field in fields:
        if field.remote_field:
            remote_field = field.remote_field.name
            if isinstance(field.remote_field, ForeignKey):
                field.remote_field.model.objects.filter(**{'%s_id' % remote_field: structure_pk}).update(**{remote_field: 1})


class Migration(migrations.Migration):

    dependencies = [
        ('authent', '0004_auto_20200211_1011'),
    ]

    operations = [
        migrations.RunPython(fix_default_structure)
    ]
