# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trekking', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='trek',
            options={'verbose_name': 'Trek', 'verbose_name_plural': 'Treks'},
        ),
        migrations.AlterField(
            model_name='servicetype',
            name='practices',
            field=models.ManyToManyField(related_name='services', db_table=b'o_r_service_pratique', verbose_name='Practices', to='trekking.Practice', blank=True),
        ),
        migrations.AlterField(
            model_name='trek',
            name='accessibilities',
            field=models.ManyToManyField(related_name='treks', db_table=b'o_r_itineraire_accessibilite', verbose_name='Accessibility', to='trekking.Accessibility', blank=True),
        ),
        migrations.AlterField(
            model_name='trek',
            name='information_desks',
            field=models.ManyToManyField(related_name='treks', to='tourism.InformationDesk', db_table=b'o_r_itineraire_renseignement', blank=True, help_text='Where to obtain information', verbose_name='Information desks'),
        ),
        migrations.AlterField(
            model_name='trek',
            name='networks',
            field=models.ManyToManyField(related_name='treks', to='trekking.TrekNetwork', db_table=b'o_r_itineraire_reseau', blank=True, help_text='Hiking networks', verbose_name='Networks'),
        ),
        migrations.AlterField(
            model_name='trek',
            name='themes',
            field=models.ManyToManyField(related_name='treks', to='common.Theme', db_table=b'o_r_itineraire_theme', blank=True, help_text='Main theme(s)', verbose_name='Themes'),
        ),
        migrations.AlterField(
            model_name='trek',
            name='web_links',
            field=models.ManyToManyField(related_name='treks', to='trekking.WebLink', db_table=b'o_r_itineraire_web', blank=True, help_text='External resources', verbose_name='Web links'),
        ),
    ]
