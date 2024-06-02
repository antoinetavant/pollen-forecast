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
pn.extension(design="material", sizing_mode="stretch_width")

POLLEN_TRANSLATIONS = {
    "apg_conc": "Aulne",  #"Alder Pollen",
    "bpg_conc": "Bouleau",  #"Birch Pollen",
    "gpg_conc": "Graminées",  #"Grass Pollen",
    "mpg_conc": "Armoise",  #"Mugwort Pollen",
    "opg_conc": "Olive", #"Olive Pollen",
    "rwpg_conc": "Ambroisie", #"Ragweed Pollen",
}
# @pn.cache
def get_data():
    today = pd.Timestamp("today").floor("D").strftime("%Y-%m-%d")
    my_api = PollenForcastCopernicusGeneric(
        start=today,
        variable=[
            "alder_pollen",
            "birch_pollen",
            "grass_pollen",
            "mugwort_pollen",
            "olive_pollen",
            "ragweed_pollen",
        ],
    )
    if not my_api.filename.exists():
        my_api.get_pollen_data()
    return my_api.pollen_data().rename(columns=POLLEN_TRANSLATIONS)


data = get_data()


def transform_data(variable, normalization=False):
    """Calculates the rolling average and identifies outliers"""
    selection = data[variable]
    if normalization:
        for col in selection.columns:
            selection[col] = selection[col] / selection[col].max()
    return selection


def get_plot(variable="Graminées", normalization=False):
    """Plots the rolling average and the outliers"""
    avg = transform_data(variable, normalization=normalization)
    return avg.hvplot(height=300, legend=False, color=PRIMARY_COLOR)


variable_widget = pn.widgets.CheckBoxGroup(
    name="variable", value=["Graminées"], options=list(data.columns)
)
normalization_widget = pn.widgets.Checkbox(
    name="Normalize", value=False
)

bound_plot = pn.bind(get_plot, variable=variable_widget, normalization=normalization_widget)


pn.template.MaterialTemplate(
    site="Météo Pollen",
    title="Prévision du pollen",
    sidebar=[variable_widget],
    main=[bound_plot],
).servable()
