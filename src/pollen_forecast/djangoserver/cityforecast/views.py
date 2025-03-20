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
    print(ip)
    location = get_location(ip)
    print(location)
    

    if request.method == "POST":
        # Get data from POST request
        selected_date = request.POST.get("date", today)
        city_name = request.POST.get("city_name", location["city"])

        lat, lon = get_city_location(city_name)

        list_of_prefectures = pd.DataFrame.from_records(
            City.objects.filter(is_prefecture=True).values(
                "official_city_name", "latitude", "longitude"
            )
        ).rename(columns={"official_city_name": "Nom Officiel Commune"})
        prefecture_name, lat, lon = find_closest_prefectures(
            lat, lon, list_of_prefectures
        )
        print(prefecture_name)
        # Fetch pollen data using the PollenConcentrationForecasted model

        pollen_data = PollenConcentrationForecasted.objects.filter(
            cityname=prefecture_name, forecasted_at=today
        ).values()

        # Convert the queryset to a pandas DataFrame
        data = pd.DataFrame.from_records(pollen_data)
        if data.empty:
            logger.warning(
                "the data has not be fetched. Fetching now. Check the scheduled task."
            )
            load_pollen_data_for_prefectures()
            pollen_data = PollenConcentrationForecasted.objects.filter(
                cityname=prefecture_name, forecasted_at=today
            ).values()

            # Convert the queryset to a pandas DataFrame
            data = pd.DataFrame.from_records(pollen_data)
        print(data["time"])
        data = data.pivot_table(index="time", columns="pollen_type", values="value")
        print(data)
        # Define levels and categories
        levels_graminees = [0, 4, 19, 50, 100, 9999]
        levels_herbes = [0, 9, 50, 100, 250, 9999]
        levels_arbres = [0, 15, 90, 250, 1500, 9999]
        level_names = ["faible", "moderé", "modéré-fort", "fort", "très fort"]
        list_herbes = ["Ambroisie", "Armoise"]
        list_arbes = ["Aulne", "Bouleau", "Olive"]
        list_graminees = ["Graminées"]

        # Add level names to data for chart coloring
        for list_pollen, levels in zip(
            [list_herbes, list_arbes, list_graminees],
            [levels_herbes, levels_arbres, levels_graminees],
        ):
            for pollen in list_pollen:
                niveau_name = f"{pollen}_niveau"
                data[niveau_name] = pd.cut(data[pollen], levels, labels=level_names)

        # Get the selected pollen type
        polen_type = request.POST.get("polen_type", "Graminées")

        # Create an Altair chart
        chart = (
            alt.Chart(data.reset_index())
            .mark_bar()
            .encode(
                y=polen_type,
                x=alt.X("time", title="Date"),
                color=alt.Color(
                    f"{polen_type}_niveau",
                    scale=alt.Scale(
                        domain=level_names,
                        range=["green", "gold", "orange", "red", "purple"],
                    ),
                    title="Niveau de risque",
                ),
            )
        )

        # Convert the chart to JSON for the front-end
        chart_json = chart.to_json()

        # Send JSON response (for AJAX call or front-end rendering)
        return JsonResponse(
            {
                "chart": chart_json,
                "city_name": city_name,
                "date": selected_date,
                "polen_type": polen_type,
            }
        )

    # If GET request, render the initial page with basic context
    context = {
        "today": today.strftime("%Y-%m-%d"),  # Format the date for HTML input
        "list_of_pollen_names": list_of_pollen_names,
        "city_estimation": location["city"],
    }

    return render(request, "cityforecast/meteoville.html", context)
