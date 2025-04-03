from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0014_auto_20171113_1827"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="sensitivearea",
            options={
                "verbose_name": "Sensitive area",
                "verbose_name_plural": "Sensitive areas",
                "permissions": (("import_sensitivearea", "Can import Sensitive area"),),
            },
        ),
    ]
