import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0009_auto_20171025_1150"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sensitivearea",
            name="email",
        ),
        migrations.AddField(
            model_name="sensitivearea",
            name="contact",
            field=models.TextField(verbose_name="Contact", blank=True),
        ),
        migrations.AlterField(
            model_name="sensitivearea",
            name="species",
            field=models.ForeignKey(
                db_column="espece",
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name="Sensitive area",
                to="sensitivity.Species",
            ),
        ),
    ]
