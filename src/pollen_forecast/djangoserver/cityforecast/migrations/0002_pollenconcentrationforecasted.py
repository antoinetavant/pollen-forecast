# Generated by Django 5.1.7 on 2025-03-20 15:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cityforecast', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PollenConcentrationForecasted',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('forecasted_at', models.DateField(default=None, help_text='The date and time when the forecast was made.')),
                ('time', models.DateTimeField(default=None, help_text='The date and time for which the forecast is valid.')),
                ('cityname', models.CharField(help_text='The official name of the city.', max_length=255)),
                ('pollen_type', models.CharField(help_text='the pollen type', max_length=255)),
                ('value', models.FloatField(default=None, verbose_name='concentration of the pollen')),
            ],
        ),
    ]
