# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tourism', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='touristiccontent',
            name='themes',
            field=models.ManyToManyField(related_name='touristiccontents', to='common.Theme', db_table=b't_r_contenu_touristique_theme', blank=True, help_text='Main theme(s)', verbose_name='Themes'),
        ),
        migrations.AlterField(
            model_name='touristicevent',
            name='themes',
            field=models.ManyToManyField(related_name='touristic_events', to='common.Theme', db_table=b't_r_evenement_touristique_theme', blank=True, help_text='Main theme(s)', verbose_name='Themes'),
        ),
    ]
