import json
from django.contrib.gis.db import models
import csv
import os
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import logging
from pollen_forecast.pollen import POLLEN_TRANSLATIONS

logger = logging.getLogger(__name__)


# Create your models here.


class Departements(models.Model):
    """Store the informations related to the departements."""

    name = models.CharField(max_length=255, help_text="the name of the departement")
    coordinates = models.TextField(
        verbose_name="Coordinate of the shape of the departement",
        help_text="Serealised of the liste fo the points",
    )
    code = models.CharField(max_length=4, help_text="The Code of the departement")
    geometry_type = models.CharField(
        max_length=255, help_text="the type of coordinate geometry", default=""
    )

    @staticmethod
    def populate_from_geojson():
        """
        Populates the City model with data from a geojson file located in the
        'data' folder. The file should have the following structure:
        {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [
                                3.172704445659,
                                50.011996744997
                            ],
                            ...
                        ]
                                    ]
            },
            ...
                    ]
        """
        logger.info("loading deparemetns")
        geojson_path = os.path.join(
            os.path.dirname(__file__), "../../../../data/departements.geojson"
        )
        with open(geojson_path, encoding="utf-8") as f:
            deps_dict = json.load(f)
        deps = []
        for feature in deps_dict["features"]:
            dep = Departements(
                name=feature["properties"]["nom"],
                code=feature["properties"]["code"],
                coordinates=json.dumps(feature["geometry"]["coordinates"]),
                geometry_type=feature["geometry"]["type"],
            )
            deps.append(dep)

        Departements.objects.bulk_create(deps, ignore_conflicts=True)


class City(models.Model):
    """
    Represents a city with its official department name, official city name,
    geographical coordinates (latitude and longitude), and whether it is a prefecture.
    """

    official_department_name = models.CharField(
        max_length=255, help_text="The official name of the department."
    )
    official_city_name = models.CharField(
        max_length=255, help_text="The official name of the city."
    )
    latitude = models.FloatField(help_text="The latitude of the city.")
    longitude = models.FloatField(help_text="The longitude of the city.")
    is_prefecture = models.BooleanField(
        help_text="Indicates if the city is a prefecture.", default=False
    )
    is_sous_prefecture = models.BooleanField(
        help_text="Indicates if the city is a sous-prefecture.", default=False
    )
    departement = models.ForeignKey(
        Departements,
        on_delete=models.CASCADE,
        related_name="cities",
        help_text="The department to which the city belongs.",
        default=None,
    )
    population = models.PositiveIntegerField(
        verbose_name="The population of the city at the 2021 sensus", default=None
    )
    location = models.PointField(
        geography=True,
        help_text="The geographical location of the city.",
        default=None,
    )

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
        - population
        - is_prefecture
        - is_sous_prefecture
        """
        logger.info("loading cities")
        csv_path = os.path.join(
            os.path.dirname(__file__), "../../../../data/georef-france-commune.csv"
        )
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            cities = []
            for row in reader:
                if not (row["is_prefecture"] or row["is_sous_prefecture"]):
                    # do not upload a city that is not relevante
                    continue
                try:
                    departement = Departements.objects.get(
                        name__iexact=row["Nom Officiel Département"]
                    )
                except Departements.DoesNotExist:
                    logger.warning(
                        f"Departement '{row['Nom Officiel Département']}' not found. Skipping city '{row['Nom Officiel Commune']}'."
                    )
                    continue
                if row["population"] == "":
                    population = 1
                else:
                    population = float(row["population"])
                city = City(
                    official_department_name=row["Nom Officiel Département"],
                    official_city_name=row["Nom Officiel Commune"],
                    latitude=float(row["latitude"]),
                    longitude=float(row["longitude"]),
                    location=f"SRID=4326;POINT({row['longitude']} {row['latitude']})",
                    is_prefecture=row["is_prefecture"].lower() == "true",
                    is_sous_prefecture=row["is_sous_prefecture"].lower() == "true",
                    departement=departement,
                    population=population,
                )
                cities.append(city)

            City.objects.bulk_create(cities, ignore_conflicts=True)


class PollenConcentrationForecasted(models.Model):
    """the pollen forcasted"""

    forecasted_at = models.DateField(
        default=None, help_text="The date and time when the forecast was made."
    )
    time = models.DateTimeField(
        default=None, help_text="The date and time for which the forecast is valid."
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="pollenconcentrationforecasted",
        help_text="The city for which the pollen forecast is made.",
        default=None,
    )
    pollen_type = models.CharField(max_length=255, help_text="the pollen type")
    value = models.FloatField(
        verbose_name="concentration of the pollen",
        default=None,
    )

    class Meta:
        indexes = [
            models.Index(fields=["city", "forecasted_at", "pollen_type"]),
            # models.Index(fields=["forecasted_at"]),
            # models.Index(fields=["cityname"]),
        ]


class PollenConcentrationHistory(models.Model):
    """the pollen forcasted"""

    time = models.DateTimeField(
        default=None, help_text="The date and time for which the forecast is valid."
    )
    pollen_type = models.CharField(max_length=255, help_text="the pollen type")
    value = models.FloatField(
        verbose_name="concentration of the pollen",
        default=None,
    )

    @staticmethod
    def populate_from_csv():
        """
        Populates the model with data from a CSV file located in the
        'data' folder. The CSV file should have the following columns:
        """
        logger.info("loading historical data")
        csv_path = os.path.join(
            os.path.dirname(__file__), "../../../../data/daily_mean_pollen_2023.csv"
        )
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            pollens = []
            for row in reader:
                for key, name in POLLEN_TRANSLATIONS.items():
                    pollen = PollenConcentrationHistory(
                        time=row["time"], pollen_type=name, value=row[key]
                    )
                    pollens.append(pollen)

            PollenConcentrationHistory.objects.bulk_create(
                pollens, ignore_conflicts=True
            )


# Signal to populate the database after migrations


@receiver(post_migrate)
def populate_cities(sender, **kwargs):
    """
    Signal handler to populate the City model with data from the CSV file
    after migrations are applied, if the model is empty.
    """
    if sender.name == "cityforecast":
        if not Departements.objects.exists():
            Departements.populate_from_geojson()
        if not City.objects.exists():
            City.populate_from_csv()
        if not PollenConcentrationHistory.objects.exists():
            PollenConcentrationHistory.populate_from_csv()
