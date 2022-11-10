# Generated by Django 3.2.15 on 2022-09-21 13:47

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('infrastructure', '0031_auto_20220921_1542'),
    ]

    operations = [
        migrations.AddField(
            model_name='infrastructuretype',
            name='date_insert',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Insertion date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='infrastructuretype',
            name='date_update',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Update date'),
        ),
        migrations.AddField(
            model_name='infrastructureusagedifficultylevel',
            name='date_insert',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='Insertion date'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='infrastructureusagedifficultylevel',
            name='date_update',
            field=models.DateTimeField(auto_now=True, db_index=True, verbose_name='Update date'),
        ),
    ]