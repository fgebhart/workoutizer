# Generated by Django 3.1.5 on 2021-01-28 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("wizer", "0002_auto_20210128_1814"),
    ]

    operations = [
        migrations.AddField(
            model_name="sport",
            name="suitable_for_best_sections",
            field=models.BooleanField(default=True, verbose_name="Find Awards for this Sport:"),
        ),
        migrations.AlterField(
            model_name="activity",
            name="suitable_for_best_sections",
            field=models.BooleanField(default=True, verbose_name="Find Awards for this Activity:"),
        ),
    ]
