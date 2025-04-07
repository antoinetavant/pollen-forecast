from django.urls import include, path
from . import views
from .api import (
    CityAutocompleteAPI,
    PollenDataAPI,
    DepartementGeoJSONAPI,
    PollenHistoryAPI,
)

urlpatterns = [
    path("", views.pollen_forecast_view, name="ville"),
    path("about", views.about_view, name="about"),
    path("history", views.history_view, name="history"),
    path("map", views.map_view, name="map"),
    path(
        "api/city-autocomplete/",
        CityAutocompleteAPI.as_view(),
        name="city_autocomplete_api",
    ),
    path(
        "api/departements-geojson/",
        DepartementGeoJSONAPI.as_view(),
        name="departements_geojson_api",
    ),
    path("api/pollen-data/", PollenDataAPI.as_view(), name="pollen_data_api"),
    path(
        "api/pollen-history-data/",
        PollenHistoryAPI.as_view(),
        name="pollen_history_data_api",
    ),
    path("silk/", include("silk.urls", namespace="silk")),
]
