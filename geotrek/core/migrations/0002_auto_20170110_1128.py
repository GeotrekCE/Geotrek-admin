# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='path',
            name='networks',
            field=models.ManyToManyField(related_name='paths', db_table=b'l_r_troncon_reseau', verbose_name='Networks', to='core.Network', blank=True),
        ),
        migrations.AlterField(
            model_name='path',
            name='usages',
            field=models.ManyToManyField(related_name='paths', db_table=b'l_r_troncon_usage', verbose_name='Usages', to='core.Usage', blank=True),
        ),
    ]
