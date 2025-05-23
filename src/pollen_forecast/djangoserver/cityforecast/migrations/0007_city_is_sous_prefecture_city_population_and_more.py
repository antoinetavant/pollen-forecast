# Generated by Django 5.1.7 on 2025-03-27 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cityforecast', '0006_departements_geometry_type_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='is_sous_prefecture',
            field=models.BooleanField(default=False, help_text='Indicates if the city is a sous-prefecture.'),
        ),
        migrations.AddField(
            model_name='city',
            name='population',
            field=models.PositiveIntegerField(default=None, verbose_name='The population of the city at the 2021 sensus'),
        ),
        migrations.AlterField(
            model_name='city',
            name='is_prefecture',
            field=models.BooleanField(default=False, help_text='Indicates if the city is a prefecture.'),
        ),
    ]
