import pandas as pd
import altair as alt
from django.shortcuts import render
from django.http import JsonResponse
from pollen_forecast.cities import (
    find_closest_city,
    get_city_location,
    # search_closest_city,
)
from pollen_forecast.pollen import get_data_at_location, list_of_pollen_names
from .geo import get_client_ip, get_location
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt

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

        # Geolocation (latitude, longitude) - optional POST data
        lat = request.POST.get("lat", location["latitude"])
        lon = request.POST.get("lon", location["longitude"])

        # If lat and lon are provided, find the closest city
        if lat and lon:
            lat = float(lat)
            lon = float(lon)
            city_name = find_closest_city(lat, lon)
        else:
            lat, lon = get_city_location(city_name)

        # Fetch pollen data
        data = get_data_at_location(selected_date, lat, lon)

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
        "today": today,
        "list_of_pollen_names": list_of_pollen_names,
        "city_estimation": location["city"],
    }

    return render(request, "cityforecast/meteoville.html", context)
