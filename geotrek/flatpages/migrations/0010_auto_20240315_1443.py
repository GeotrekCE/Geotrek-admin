from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0036_accessmean'),
        ('flatpages', '0009_auto_20210121_0943'),
    ]

    operations = [
        migrations.CreateModel(
            name='MenuItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_insert', models.DateTimeField(auto_now_add=True, verbose_name='Insertion date')),
                ('date_update', models.DateTimeField(auto_now=True, db_index=True, verbose_name='Update date')),
                ('published',
                 models.BooleanField(default=False, help_text='Visible on Geotrek-rando', verbose_name='Published')),
                ('publication_date',
                 models.DateField(blank=True, editable=False, null=True, verbose_name='Publication date')),
                ('pictogram',
                 models.FileField(blank=True, max_length=512, null=True, upload_to='upload', verbose_name='Pictogram')),
                ('path', models.CharField(max_length=255, unique=True)),
                ('depth', models.PositiveIntegerField()),
                ('numchild', models.PositiveIntegerField(default=0)),
                ('label', models.CharField(max_length=50, verbose_name='Label')),
                ('target_type',
                 models.CharField(choices=[('page', 'Page'), ('link', 'Link')], max_length=10, null=True)),
                ('link_url', models.URLField(blank=True, default='', verbose_name='Link URL')),
                ('platform',
                 models.CharField(choices=[('all', 'All'), ('mobile', 'Mobile'), ('web', 'Web')], default='all',
                                  max_length=12, verbose_name='Platform')),
                ('open_in_new_tab', models.BooleanField(default=False, verbose_name='Open the link in a new tab')),
                ('page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                                           related_name='menu_items', to='flatpages.flatpage')),
                ('portals', models.ManyToManyField(blank=True, related_name='menu_items', to='common.TargetPortal',
                                                   verbose_name='Portal')),
            ],
            options={
                'verbose_name': 'Menu item',
                'verbose_name_plural': 'Menu items',
            },
        ),
    ]
