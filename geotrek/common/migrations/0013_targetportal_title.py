# Generated by Django 2.2.16 on 2020-09-17 13:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("common", "0012_reservationsystem"),
    ]

    operations = [
        migrations.AddField(
            model_name="targetportal",
            name="title",
            field=models.CharField(
                default="",
                help_text="Title on Geotrek Rando",
                max_length=50,
                verbose_name="Title Rando",
            ),
        ),
        migrations.AddField(
            model_name="targetportal",
            name="description",
            field=models.TextField(
                default="",
                help_text="Description on Geotrek Rando",
                verbose_name="Description",
            ),
        ),
        migrations.AddField(
            model_name="targetportal",
            name="facebook_id",
            field=models.CharField(
                blank=True,
                help_text="Facebook ID for Geotrek Rando",
                max_length=20,
                null=True,
                verbose_name="Facebook ID",
            ),
        ),
        migrations.AddField(
            model_name="targetportal",
            name="facebook_image_height",
            field=models.IntegerField(
                default=200,
                help_text="Facebook image's height",
                verbose_name="Facebook image height",
            ),
        ),
        migrations.AddField(
            model_name="targetportal",
            name="facebook_image_url",
            field=models.CharField(
                default="/images/logo-geotrek.png",
                help_text="Url of the facebook image url",
                max_length=256,
                verbose_name="Facebook image url",
            ),
        ),
        migrations.AddField(
            model_name="targetportal",
            name="facebook_image_width",
            field=models.IntegerField(
                default=200,
                help_text="Facebook image's width",
                verbose_name="Facebook image width",
            ),
        ),
    ]
