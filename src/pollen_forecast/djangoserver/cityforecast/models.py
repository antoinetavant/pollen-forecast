from django.db import models
import csv
import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

# Create your models here.
class City(models.Model):
    """
    Represents a city with its official department name, official city name,
    geographical coordinates (latitude and longitude), and whether it is a prefecture.
    """
    official_department_name = models.CharField(max_length=255, help_text="The official name of the department.")
    official_city_name = models.CharField(max_length=255, help_text="The official name of the city.")
    latitude = models.FloatField(help_text="The latitude of the city.")
    longitude = models.FloatField(help_text="The longitude of the city.")
    is_prefecture = models.BooleanField(help_text="Indicates if the city is a prefecture.")

    def __str__(self):
        """
        Returns a string representation of the city in the format:
        'City Name, Department Name'.
        """
        return f"{self.official_city_name}, {self.official_department_name}"

    @staticmethod
    def populate_from_csv():
        """
        Populates the City model with data from a CSV file located in the
        'data' folder. The CSV file should have the following columns:
        - Nom Officiel Département
        - Nom Officiel Commune
        - latitude
        - longitude
        - Is Prefecture
        """
        csv_path = os.path.join(os.path.dirname(__file__), '../../../../data/georef-france-commune.csv')
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                City.objects.get_or_create(
                    official_department_name=row['Nom Officiel Département'],
                    official_city_name=row['Nom Officiel Commune'],
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    is_prefecture=row['is_prefecture'].lower() == 'true'
                )

# Signal to populate the database after migrations

@receiver(post_migrate)
def populate_cities(sender, **kwargs):
    """
    Signal handler to populate the City model with data from the CSV file
    after migrations are applied, if the model is empty.
    """
    if sender.name == 'cityforecast':
        if not City.objects.exists():
            City.populate_from_csv()