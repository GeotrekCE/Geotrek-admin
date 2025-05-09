# Generated by Django 3.2.15 on 2022-11-10 10:28
import os
import shutil

from django.conf import settings
from django.db import migrations


def flush_cache(apps, schema_editor):
    """Flush cache for make new system available"""
    shutil.rmtree(settings.CACHE_ROOT)
    os.mkdir(settings.CACHE_ROOT)
    os.mkdir(os.path.join(settings.CACHE_ROOT, "sessions"))
    os.mkdir(os.path.join(settings.CACHE_ROOT, "fat"))
    os.mkdir(os.path.join(settings.CACHE_ROOT, "api_v2"))


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0026_auto_20221110_1128"),
    ]

    operations = [migrations.RunPython(flush_cache, migrations.RunPython.noop)]
