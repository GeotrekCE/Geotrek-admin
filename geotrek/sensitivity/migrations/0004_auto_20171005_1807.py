from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sensitivity", "0003_auto_20171005_1801"),
    ]

    operations = [
        migrations.AddField(
            model_name="sensitivearea",
            name="description",
            field=models.TextField(verbose_name="Description", blank=True),
        ),
        migrations.AddField(
            model_name="sensitivearea",
            name="email",
            field=models.EmailField(max_length=254, verbose_name="Email", blank=True),
        ),
    ]
