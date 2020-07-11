# Generated by Django 3.0.8 on 2020-07-09 05:42

from django.db import migrations, models
import django.db.models.deletion
import wizer.models


class Migration(migrations.Migration):

    dependencies = [
        ('wizer', '0002_auto_20200704_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='sport',
            field=models.ForeignKey(default=wizer.models.default_sport, on_delete=django.db.models.deletion.SET_DEFAULT, to='wizer.Sport', verbose_name='Sport:'),
        ),
    ]
