# Generated by Django 3.0.8 on 2020-12-30 09:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("wizer", "0009_auto_20201230_0827"),
    ]

    operations = [
        migrations.RenameField(
            model_name="bestsection",
            old_name="secion_type",
            new_name="section_type",
        ),
    ]