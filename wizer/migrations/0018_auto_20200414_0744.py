# Generated by Django 3.0.3 on 2020-04-14 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizer', '0017_settings_delete_files_after_import'),
    ]

    operations = [
        migrations.AlterField(
            model_name='settings',
            name='reimporter_updates_all',
            field=models.BooleanField(default=False, verbose_name='Force Update all Fields:'),
        ),
    ]