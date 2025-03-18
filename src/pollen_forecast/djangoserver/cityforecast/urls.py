from django.urls import path

from . import views

urlpatterns = [
    path("", views.pollen_forecast_view, name="ville"),
]
