from django.urls import path
from . import views
from .api import CityAutocompleteAPI, PollenDataAPI

urlpatterns = [
    path("", views.pollen_forecast_view, name="ville"),
    path(
        "api/city-autocomplete/",
        CityAutocompleteAPI.as_view(),
        name="city_autocomplete_api",
    ),
    path("api/pollen-data/", PollenDataAPI.as_view(), name="pollen_data_api"),
]
