# Generated by Django 2.2.5 on 2020-02-08 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('wizer', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='traces',
            old_name='altitude',
            new_name='elevation',
        ),
    ]