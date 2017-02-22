# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import embed_video.fields
import paperclip.models
from django.conf import settings
import geotrek.authent.models


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('authent', '0001_initial'),
        ('cirkwi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('attachment_file', models.FileField(upload_to=paperclip.models.attachment_upload, max_length=512, verbose_name='File', blank=True)),
                ('attachment_video', embed_video.fields.EmbedVideoField(verbose_name='URL', blank=True)),
                ('author', models.CharField(db_column=b'auteur', default=b'', max_length=128, blank=True, help_text='Original creator', verbose_name='Author')),
                ('title', models.CharField(db_column=b'titre', default=b'', max_length=128, blank=True, help_text='Renames the file', verbose_name='Filename')),
                ('legend', models.CharField(db_column=b'legende', default=b'', max_length=128, blank=True, help_text='Details displayed', verbose_name='Legend')),
                ('starred', models.BooleanField(default=False, help_text='Mark as starred', verbose_name='Starred', db_column=b'marque')),
                ('date_insert', models.DateTimeField(auto_now_add=True, verbose_name='Insertion date')),
                ('date_update', models.DateTimeField(auto_now=True, verbose_name='Update date')),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('creator', models.ForeignKey(related_name='created_attachments', verbose_name='Creator', to=settings.AUTH_USER_MODEL, help_text='User that uploaded')),
            ],
            options={
                'ordering': ['-date_insert'],
                'abstract': False,
                'verbose_name_plural': 'Attachments',
                'db_table': 'fl_t_fichier',
                'default_permissions': (),
                'verbose_name': 'Attachment',
                'permissions': (('add_attachment', 'Can add attachments'), ('change_attachment', 'Can change attachments'), ('delete_attachment', 'Can delete attachments'), ('read_attachment', 'Can read attachments'), ('delete_attachment_others', "Can delete others' attachments")),
            },
        ),
        migrations.CreateModel(
            name='FileType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=128, verbose_name='File type')),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'ordering': ['type'],
                'abstract': False,
                'db_table': 'fl_b_fichier',
                'verbose_name': 'File type',
                'verbose_name_plural': 'File types',
            },
        ),
        migrations.CreateModel(
            name='Organism',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('organism', models.CharField(max_length=128, verbose_name='Organism', db_column=b'organisme')),
                ('structure', models.ForeignKey(db_column=b'structure', default=geotrek.authent.models.default_structure_pk, verbose_name='Related structure', to='authent.Structure')),
            ],
            options={
                'ordering': ['organism'],
                'db_table': 'm_b_organisme',
                'verbose_name': 'Organism',
                'verbose_name_plural': 'Organisms',
            },
        ),
        migrations.CreateModel(
            name='RecordSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pictogram', models.FileField(db_column=b'picto', upload_to=b'upload', max_length=512, blank=True, null=True, verbose_name='Pictogram')),
                ('name', models.CharField(max_length=50, verbose_name='Name')),
                ('website', models.URLField(max_length=256, null=True, verbose_name='Website', db_column=b'website', blank=True)),
            ],
            options={
                'ordering': ['name'],
                'db_table': 'o_b_source_fiche',
                'verbose_name': 'Record source',
                'verbose_name_plural': 'Record sources',
            },
        ),
        migrations.CreateModel(
            name='TargetPortal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text='Used for sync', unique=b'True', max_length=50, verbose_name='Name')),
                ('website', models.URLField(unique=b'True', max_length=256, verbose_name='Website', db_column=b'website')),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'o_b_target_portal',
                'verbose_name': 'Target portal',
                'verbose_name_plural': 'Target portals',
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pictogram', models.FileField(max_length=512, null=True, verbose_name='Pictogram', db_column=b'picto', upload_to=b'upload')),
                ('label', models.CharField(max_length=128, verbose_name='Label', db_column=b'theme')),
                ('cirkwi', models.ForeignKey(verbose_name='Cirkwi tag', blank=True, to='cirkwi.CirkwiTag', null=True)),
            ],
            options={
                'ordering': ['label'],
                'db_table': 'o_b_theme',
                'verbose_name': 'Theme',
                'verbose_name_plural': 'Themes',
            },
        ),
        migrations.AddField(
            model_name='attachment',
            name='filetype',
            field=models.ForeignKey(verbose_name='File type', to='common.FileType'),
        ),
    ]
