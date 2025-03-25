from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from cityforecast.tasks import load_pollen_data_for_prefectures
from .models import PollenConcentrationForecasted, City
from pollen_forecast.pollen import plant_types, levels_map, level_names
from pollen_forecast.cities import find_closest_prefectures
import pandas as pd
from datetime import datetime
from django.db import connection
import logging

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
                cities = City.objects.filter(official_city_name__icontains=query)[:10]
            
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

        # Fetch pollen data
        pollen_data = PollenConcentrationForecasted.objects.filter(
            cityname=prefecture_name,
            forecasted_at=selected_date,
            pollen_type=pollen_type,
        ).values()

        # Convert the queryset to a pandas DataFrame
        data = pd.DataFrame.from_records(pollen_data)
        if data.empty:
            logger.warning(
                "the data has not be fetched. Fetching now. Check the scheduled task."
            )
            load_pollen_data_for_prefectures()
            pollen_data = PollenConcentrationForecasted.objects.filter(
                cityname=prefecture_name,
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