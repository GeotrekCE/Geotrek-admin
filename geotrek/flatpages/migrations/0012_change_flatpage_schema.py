from django.db import migrations, models


def set_treebeard_path_fields(apps, schema_editor):
    FlatPage = apps.get_model('flatpages', 'FlatPage')
    pages = FlatPage.objects.all()
    for page in pages:
        page.path = str(page.pk)
        page.save()


class Migration(migrations.Migration):

    dependencies = [
        ('flatpages', '0011_migrate_flatpage_data'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='flatpage',
            options={'permissions': (('read_flatpage', 'Can read FlatPage'),), 'verbose_name': 'Flat page', 'verbose_name_plural': 'Flat pages'},
        ),
        migrations.RenameField(
            model_name='flatpage',
            old_name='portal',
            new_name='portals',
        ),
        migrations.RemoveField(
            model_name='flatpage',
            name='external_url',
        ),
        migrations.RemoveField(
            model_name='flatpage',
            name='order',
        ),
        migrations.RemoveField(
            model_name='flatpage',
            name='target',
        ),
        migrations.AddField(
            model_name='flatpage',
            name='depth',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='flatpage',
            name='numchild',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='flatpage',
            name='path',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.RunPython(set_treebeard_path_fields),
        migrations.AlterField(
            model_name='flatpage',
            name='path',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
