import embed_video.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="attachment",
            name="attachment_link",
            field=models.URLField(verbose_name="Picture URL", blank=True),
        ),
        migrations.AlterField(
            model_name="attachment",
            name="attachment_video",
            field=embed_video.fields.EmbedVideoField(
                verbose_name="Video URL", blank=True
            ),
        ),
    ]
