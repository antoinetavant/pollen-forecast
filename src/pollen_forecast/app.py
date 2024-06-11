"""Uses Holoviz panel to create a web app for the pollen forecast model."""

import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn

from copernicus import PollenForcastCopernicusGeneric


PRIMARY_COLOR = "#0072B5"
SECONDARY_COLOR = "#B54300"
CSV_FILE = (
    "https://raw.githubusercontent.com/holoviz/panel/main/examples/assets/occupancy.csv"
)
pn.extension(design="material", sizing_mode="stretch_width", loading_spinner='dots', loading_color='#00aa41')

POLLEN_TRANSLATIONS = {
    "apg_conc": "Aulne",  #"Alder Pollen",
    "bpg_conc": "Bouleau",  #"Birch Pollen",
    "gpg_conc": "Graminées",  #"Grass Pollen",
    "mpg_conc": "Armoise",  #"Mugwort Pollen",
    "opg_conc": "Olive", #"Olive Pollen",
    "rwpg_conc": "Ambroisie", #"Ragweed Pollen",
}
# @pn.cache
def get_data(date=pd.Timestamp("today").date(),
             latitude= 45.75,
             longitude= 4.85):
    print("Fetching data")
    my_api = PollenForcastCopernicusGeneric(
        start=date,
        variable=[
            "alder_pollen",
            "birch_pollen",
            "grass_pollen",
            "mugwort_pollen",
            "olive_pollen",
            "ragweed_pollen",
        ],
    north=51.70,
    south=41.87,
    east=8.74,
    west=-5.33,
    prefix="./france_territory/"
    )
    if not my_api.filename.exists():
        print("Downloading data")
        my_api.get_pollen_data()
    print(f"{latitude=}, {longitude=}")
    return my_api.pollen_data(latitude=latitude, longitude=longitude).rename(columns=POLLEN_TRANSLATIONS)



print("Fetching list of cities")
list_of_villes = pd.read_csv("georef-france-commune.csv")
print("List of cities fetched")
availables_villes = list_of_villes["Nom Officiel Commune"].unique().tolist()
print("List of cities transformed")
# champs de recherche pour villes
ville_widget = pn.widgets.AutocompleteInput(
    name="Ville",
    options=availables_villes,
    placeholder="Entrez une ville",
    case_sensitive=False,
    search_strategy='includes',
    restrict=True,
)
print("Ville widget created")


def transform_data(data, variable, normalization=False):
    """Calculates the rolling average and identifies outliers"""
    selection = data[variable]
    if normalization:
        for col in selection.columns:
            selection[col] = selection[col] / selection[col].max()
    return selection


def get_plot(variable="Graminées",
             normalization=False,
             date=pd.Timestamp("today").date(),
             commune="Lyon"):
    """Plots the rolling average and the outliers"""
    print(f"{commune=}")
    if commune == "":
        commune = "Lyon"
    ville_line = list_of_villes[ list_of_villes["Nom Officiel Commune"] == commune]
    latitude = ville_line["latitude"].values[0]
    longitude = ville_line["longitude"].values[0]
    data = get_data(date=date, latitude=latitude, longitude=longitude)
    avg = transform_data(data, variable, normalization=normalization)
    print(avg)
    # add title the commune name
    avg = avg.hvplot(height=300, legend=False, color=PRIMARY_COLOR)
    avg.opts(title=f"Prévision du pollen à {commune}")
    return avg


variable_widget = pn.widgets.CheckBoxGroup(
    name="variable", value=["Graminées"], options=list(POLLEN_TRANSLATIONS.values())
)

bound_plot = pn.param.ParamFunction(
    pn.bind(get_plot, variable=variable_widget, commune=ville_widget),
    loading_indicator=True,
)

pn.template.MaterialTemplate(
    site="Météo Pollen",
    title="Prévision du pollen",
    sidebar=[variable_widget, ville_widget],
    main=[bound_plot],
).servable()
