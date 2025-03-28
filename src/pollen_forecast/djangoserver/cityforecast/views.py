import pandas as pd
import altair as alt
from django.shortcuts import render
from django.http import JsonResponse
from pollen_forecast.cities import (
    find_closest_city,
    get_city_location,
    # search_closest_city,
    find_closest_prefectures,
)
from pollen_forecast.pollen import get_data_at_location, list_of_pollen_names
from cityforecast.tasks import load_pollen_data_for_prefectures
import json

from .geo import get_client_ip, get_location
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from .models import City
from .models import PollenConcentrationForecasted
import logging

logger = logging.getLogger(__name__)

# Cache can be added via Django cache framework if needed


def pollen_forecast_view(request):
    # Handle the date input (defaults to today)
    today = datetime.today().date()

    ip = get_client_ip(request=request)
    location = get_location(ip)
    # Find the closest prefecture as the ip geolocation is not very precise
    list_of_prefectures = pd.DataFrame.from_records(
        City.objects.filter(is_prefecture=True).values(
            "official_city_name", "latitude", "longitude"
        )
    ).rename(columns={"official_city_name": "Nom Officiel Commune"})
    prefecture_name, latitude, longitude = find_closest_prefectures(
        lat=location["latitude"],
        lon=location["longitude"],
        list_of_prefectures=list_of_prefectures,
    )

    # If GET request, render the initial page with basic context
    context = {
        "today": today.strftime("%Y-%m-%d"),  # Format the date for HTML input
        "list_of_pollen_names": list_of_pollen_names,
        "city_estimation": prefecture_name,
    }

    return render(request, "cityforecast/meteoville.html", context)

def about_view(request):
    context = {}
    return render(request, "cityforecast/about.html", context)


def map_view(request):
    # Handle the date input (defaults to today)
    today = datetime.today().date()
    context = {
        "today": today.strftime("%Y-%m-%d"),  # Format the date for HTML input
        "list_of_pollen_names": list_of_pollen_names,
    }
    return render(request, "cityforecast/map.html", context)


def history_view(request):
    # Handle the date input (defaults to today)
    context = {
        "list_of_pollen_names": list_of_pollen_names,
    }
    return render(request, "cityforecast/history.html", context)