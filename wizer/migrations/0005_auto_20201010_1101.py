# Generated by Django 3.0.8 on 2020-10-10 09:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('wizer', '0004_traces_distance_list'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='traces',
            name='coordinates_list',
        ),
        migrations.AddField(
            model_name='traces',
            name='latitude_list',
            field=models.CharField(default='[]', max_length=10000000000),
        ),
        migrations.AddField(
            model_name='traces',
            name='longitude_list',
            field=models.CharField(default='[]', max_length=10000000000),
        ),
    ]
