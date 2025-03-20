from django.urls import path
from . import views
from .api import CityAutocompleteAPI

urlpatterns = [
    path("", views.pollen_forecast_view, name="ville"),
    path(
        "api/city-autocomplete/",
        CityAutocompleteAPI.as_view(),
        name="city_autocomplete_api",
    ),
]
