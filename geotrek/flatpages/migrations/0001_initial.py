# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('common', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FlatPage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_insert', models.DateTimeField(auto_now_add=True, verbose_name='Insertion date', db_column=b'date_insert')),
                ('date_update', models.DateTimeField(auto_now=True, verbose_name='Update date', db_column=b'date_update')),
                ('published', models.BooleanField(default=False, help_text='Online', verbose_name='Published', db_column=b'public')),
                ('publication_date', models.DateField(verbose_name='Publication date', null=True, editable=False, db_column=b'date_publication', blank=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title', db_column=b'titre')),
                ('external_url', models.URLField(db_column=b'url_externe', default=b'', blank=True, help_text='Link to external website instead of HTML content', verbose_name='External URL')),
                ('content', models.TextField(help_text='HTML content', null=True, verbose_name='Content', db_column=b'contenu', blank=True)),
                ('target', models.CharField(default=b'all', max_length=12, verbose_name='Target', db_column=b'cible', choices=[(b'all', 'All'), (b'mobile', 'Mobile'), (b'hidden', 'Hidden'), (b'web', 'Web')])),
                ('order', models.IntegerField(default=None, help_text='ID order if blank', null=True, verbose_name='Order', blank=True)),
                ('portal', models.ManyToManyField(related_name='flatpages', db_table=b't_r_page_portal', verbose_name='Portal', to='common.TargetPortal', blank=True)),
                ('source', models.ManyToManyField(related_name='flatpages', db_table=b't_r_page_source', verbose_name='Source', to='common.RecordSource', blank=True)),
            ],
            options={
                'ordering': ['order', 'id'],
                'db_table': 'p_t_page',
                'verbose_name': 'Flat page',
                'verbose_name_plural': 'Flat pages',
                'permissions': (('read_flatpage', 'Can read FlatPage'),),
            },
        ),
    ]
