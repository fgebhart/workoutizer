# Generated by Django 3.2.7 on 2021-09-29 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wkz", "0008_auto_20210611_0747"),
    ]

    operations = [
        migrations.AlterField(
            model_name="settings",
            name="path_to_garmin_device",
            field=models.CharField(blank=True, default="", max_length=120, verbose_name="Path to Garmin Device"),
        ),
    ]
