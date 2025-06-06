from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from silk.profiling.profiler import silk_profile
from cityforecast.tasks import (
    load_pollen_data_for_prefectures,
    load_pollen_data_fore_one_city,
)
from .models import (
    PollenConcentrationForecasted,
    City,
    Departements,
    PollenConcentrationHistory,
)
from pollen_forecast.pollen import plant_types, levels_map, level_names
from pollen_forecast.cities import find_closest_prefectures
import pandas as pd
from datetime import datetime
from django.db import connection
import logging
from django.db.models import Max, Q
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from django.db.models import F, FloatField
import json

logger = logging.getLogger(__name__)

class CityAutocompleteAPI(APIView):
    """API endpoint to return city autocomplete suggestions."""

    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        if query:
            if connection.vendor == 'postgresql':
                # Use TrigramSimilarity for PostgreSQL
                from django.contrib.postgres.search import TrigramSimilarity
                cities = City.objects.annotate(
                    similarity=TrigramSimilarity('official_city_name', query)
                ).filter(similarity__gt=0.3).order_by('-similarity')[:10]
            else:
                # Fallback for SQLite or other databases
                cities = City.objects.filter(
                    official_city_name__icontains=query
                ).order_by("-population")[:5]
            
            city_names = list(cities.values_list("official_city_name", flat=True))
            return Response(city_names, status=status.HTTP_200_OK)
        return Response([], status=status.HTTP_200_OK)


class PollenDataAPI(APIView):
    def get(self, request, *args, **kwargs):
        # Extract query parameters
        selected_date = request.GET.get("date", datetime.today().date())
        city_name = request.GET.get("city_name", None)
        pollen_type = request.GET.get("pollen_type", None)

        if not city_name:
            return Response({"error": "City name is required"}, status=400)

        # Get city location
        try:
            city = City.objects.get(official_city_name=city_name)
            lat, lon = city.latitude, city.longitude
        except City.DoesNotExist:
            return Response({"error": "City not found"}, status=404)

        # Find the closest prefecture
        list_of_prefectures = pd.DataFrame.from_records(
            City.objects.filter(is_prefecture=True).values(
                "official_city_name", "latitude", "longitude"
            )
        ).rename(columns={"official_city_name": "Nom Officiel Commune"})
        prefecture_name, lat, lon = find_closest_prefectures(
            lat, lon, list_of_prefectures
        )
        try:
            prefecture_city = City.objects.get(official_city_name=prefecture_name)
        except City.DoesNotExist:
            return Response({"error": "Prefecture not found"}, status=404)

        # Fetch pollen data
        pollen_data = PollenConcentrationForecasted.objects.filter(
            city=prefecture_city,
            forecasted_at=selected_date,
            pollen_type=pollen_type,
        ).values()

        # Convert the queryset to a pandas DataFrame
        data = pd.DataFrame.from_records(pollen_data)
        if data.empty:
            logger.warning(
                "the data has not be fetched. Fetching now. Check the scheduled task."
            )
            # load_pollen_data_fore_one_city(today=selected_date, city=prefecture_city)
            load_pollen_data_for_prefectures(the_date=selected_date)
            pollen_data = PollenConcentrationForecasted.objects.filter(
                city=prefecture_city,
                forecasted_at=selected_date,
                pollen_type=pollen_type,
            ).values()
            # Convert the queryset to a pandas DataFrame
            data = pd.DataFrame.from_records(pollen_data)
        if data.empty:
            return Response(
                {"error": "No data available for the selected date and city"},
                status=404,
            )
        # Pivot the data for easier processing
        data = data.set_index("time")[["value"]].rename(columns={"value": pollen_type})


        # Add level names to data for chart coloring
        levels = levels_map[plant_types[pollen_type]]
        niveau_name = f"{pollen_type}_niveau"
        data[niveau_name] = pd.cut(data[pollen_type], levels, labels=level_names)

        # Convert the index (time) to strings
        data.index = data.index.strftime("%Y-%m-%dT%H:%M:%S")
        data = data.reset_index(names="time")
        return Response(data.to_dict(orient="records"))

class PollenHistoryAPI(APIView):
    def get(self, request, *args, **kwargs):
        # Extract query parameters
        pollen_type = request.GET.get("pollen_type", None)
        if pollen_type is None:
            pollen_type = "Bouleau"
        # Fetch pollen data
        pollen_data = (
            PollenConcentrationHistory.objects.filter(
                pollen_type=pollen_type,
            )
            .only("time", "value")
            .values()
        )
        # Convert the queryset to a pandas DataFrame
        data = pd.DataFrame.from_records(pollen_data)
        # Pivot the data for easier processing
        data = data.set_index("time")[["value"]].rename(columns={"value": pollen_type})

        # Add level names to data for chart coloring
        levels = levels_map[plant_types[pollen_type]]
        niveau_name = f"{pollen_type}_niveau"
        data[niveau_name] = pd.cut(
            data[pollen_type], levels, labels=level_names
        ).fillna(level_names[0])
        
        # remove duplicated indexes and sort by date
        data = data[~data.index.duplicated(keep="first")]
        data = data.sort_index()

        # Convert the index (time) to strings
        data.index = data.index.strftime("%Y-%m-%dT%H:%M:%S")
        data = data.reset_index(names="time")
        print(data)
        return Response(data.to_dict(orient="records"))

def get_color(value, pollen_type):
    levels = levels_map[plant_types[pollen_type]]
    colors = ["#29ff08", "#FD8D3C", "#FC4E2A", "#BD0026", "#800026"]
    for i, level in enumerate(levels):
        if i == 0 and value <= level:  # Inclusive lower bound for the first level
            return "#dbdbdb"  # gray
        elif (
            i > 0 and levels[i - 1] < value <= level
        ):  # Exclusive lower, inclusive upper
            return colors[i]
    return colors[-1]  # Default to the highest level color


class DepartementGeoJSONAPI(APIView):
    @silk_profile(name="DepartementGeoJSONAPI.get")
    def get(self, request, *args, **kwargs):
        # Extract query parameters
        selected_date = request.GET.get("date", datetime.today().date())
        pollen_type = request.GET.get("pollen_type", None)

        if not pollen_type:
            return Response({"error": "Pollen type is required"}, status=400)

        # Annotate departements with the max pollen concentration for the given date and pollen type
        departements = (
            Departements.objects.annotate(
                max_pollen_concentration=Max(
                    "cities__pollenconcentrationforecasted__value",
                    filter=Q(
                        cities__pollenconcentrationforecasted__forecasted_at=selected_date,
                        cities__pollenconcentrationforecasted__pollen_type=pollen_type,
                    ),
                )
            ).filter(
                max_pollen_concentration__isnull=False
            )  # Exclude departements with no data
        )
        if len(departements) == 0:
            # no data available, need to fetch
            load_pollen_data_for_prefectures()
            return self.get(request, *args, **kwargs)
        # Build the GeoJSON response
        features = []
        for departement in departements:
            # try:
            #     # Deserialize the coordinates stored as text
            #     geometry = json.loads(departement.coordinates)
            # except json.JSONDecodeError:
            #     continue  # Skip invalid geometry

            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "name": departement.name,
                        "pollen_concentration": departement.max_pollen_concentration,
                        "color": get_color(
                            departement.max_pollen_concentration, pollen_type
                        ),
                    },
                    "geometry": {
                        "type": departement.geometry_type,
                        "coordinates": departement.coordinates,
                    },
                }
            )

        geojson = {
            "type": "FeatureCollection",
            "features": features,
        }

        response = JsonResponse(
            geojson,
            safe=False,
            json_dumps_params={"indent": 2},
            encoder=DjangoJSONEncoder,
        )
        # Remove string quotes from geometry coordinates in the dumped JSON
        # this is more like an hack that proper, but I don't what to seralize and desearize all the coordinates
        response.content = response.content.replace(
            b'"coordinates": "', b'"coordinates": '
        ).replace(b']"\n', b"]\n")
        return response



class ReverseGeocodeAPI(APIView):
    """API endpoint to return the closest city based on latitude and longitude."""

    def get(self, request, *args, **kwargs):
        latitude = request.GET.get("lat", None)
        longitude = request.GET.get("lon", None)

        if not latitude or not longitude:
            return Response({"error": "Latitude and longitude are required"}, status=400)

        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except ValueError:
            return Response({"error": "Invalid latitude or longitude"}, status=400)

        user_location = Point(longitude, latitude, srid=4326)
        print(user_location)

        # Find the closest city using the City model
        closest_city = (
            City.objects.annotate(
                distance=Distance("location", user_location)
            )
            .order_by("distance")
            .first()
        )

        if closest_city:
            return Response(
                {"city": closest_city.official_city_name}, status=status.HTTP_200_OK
            )
        else:
            return Response({"error": "No city found near the given location"}, status=404)
