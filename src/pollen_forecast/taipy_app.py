"""Launch a dashboard with two pages: one for the sun flux and one for the wind speed.

This is a simple, first version of the dashboard.

Usage:
>>> python src/dashboard/dashboard.py

This will download the data and display the dashboard in the browser.

"""
from taipy.gui import Gui, notify
import taipy.gui.builder as tgb
import pandas as pd
from pollen_forecast.copernicus import PollenForcastCopernicusGeneric
import logging
import difflib

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s][APP][%(levelname)s] %(message)s',
                              "%Y-%m-%d %H:%M:%S")
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)



# Define the translations for the pollen variables
POLLEN_TRANSLATIONS = {
    "apg_conc": "Aulne",  #"Alder Pollen",
    "bpg_conc": "Bouleau",  #"Birch Pollen",
    "gpg_conc": "Graminées",  #"Grass Pollen",
    "mpg_conc": "Armoise",  #"Mugwort Pollen",
    "opg_conc": "Olive", #"Olive Pollen",
    "rwpg_conc": "Ambroisie", #"Ragweed Pollen",
}

list_of_pollen_names = list(POLLEN_TRANSLATIONS.values())

selected_pollen = "Bouleau"


def fetch_pollen_data(date):
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
        logger.debug("Downloading Copernicus data")
        my_api.get_pollen_data()
    return my_api


def transform_data(data, variable):
    """Calculates the rolling average and identifies outliers"""
    selection = data[variable]
    return selection.reset_index()

def get_data(date=(pd.Timestamp("today") - pd.Timedelta("8h")).date(),
             latitude= 45.75,
             longitude= 4.85):
    logger.debug("Fetching data")
    my_api = fetch_pollen_data(date)
    logger.debug(f"{latitude=}, {longitude=}")
    return my_api.pollen_data(latitude=latitude, longitude=longitude).rename(columns=POLLEN_TRANSLATIONS)



def load_city_list():
    logger.debug("Fetching list of cities")
    list_of_villes = pd.read_csv("georef-france-commune.csv")
    availables_villes = list_of_villes["Nom Officiel Commune"].unique().tolist()
    return list_of_villes, sorted(availables_villes)

list_of_villes, availables_villes = load_city_list()
selected_ville = "Lyon"

def get_plot_data(variable="Graminées",
             commune="Lyon",
             ):
    """Plots the rolling average and the outliers"""
    logger.debug(f"{commune=}")
    if commune == "":
        commune = "Lyon"
    ville_line = list_of_villes[ list_of_villes["Nom Officiel Commune"] == commune]
    latitude = ville_line["latitude"].values[0]
    longitude = ville_line["longitude"].values[0]
    data = get_data(latitude=latitude, longitude=longitude)
    logger.debug(f"{data=}")
    avg = transform_data(data, variable)
    avg.rename(columns={variable: "Concentration de pollen"}, inplace=True)
    logger.debug(f"{avg=}")
    return avg

data_pollen = get_plot_data(variable=selected_pollen)

def on_chang_pollen_selection(state, var_name, var_value):
    logger.debug(f"Changing pollen selection to {var_value}")
    notify(state, "info", "Changing pollen selection")
    state.selected_pollen = var_value
    state.data_pollen = get_plot_data(variable=var_value)

def on_change_ville_selection(state, var_name, var_value):
    logger.debug(f"Changing ville selection to {var_value}")
    notify(state, "info", "Changing ville selection")
    provided_ville = var_value
    closest_ville = difflib.get_close_matches(provided_ville, availables_villes, n=1)
    if len(closest_ville) == 0:
        notify(state, "error", f"Ville {provided_ville} not found")
        return
    state.selected_ville = closest_ville[0]
    state.data_pollen = get_plot_data(variable=state.selected_pollen, commune=var_value)

# Add a navbar to switch from one page to the other
with tgb.Page() as root_page:
    tgb.text("# Predictions de Pollen", mode="md")


def plotly_figure(data):
    import plotly.graph_objects as go

    figure = go.Figure()
    for col in data.columns:
        figure.add_trace(go.Scatter(
            x=data.index,
            y=data[col],
            mode='lines',
            name=col,
        ))
    return figure

figure = plotly_figure(data_pollen)

with tgb.Page() as page_pollen:
    tgb.text(value="Prévision de la concentration de pollen" , mode="md")
    tgb.text("Sélectionnez une ville et un type de pollen pour afficher les prévisions")
    with tgb.layout(columns="1  1"):
        tgb.input(value="{selected_ville}",
                label="Ville",
                on_change=on_change_ville_selection,
                )
        # tgb.selector(value="{selected_ville}",
        #             lov=availables_villes[:10],
        #             label="Ville",
        #             dropdown=True,
        #             class_name="ville_selector",
        #             )

        tgb.selector(value="{selected_pollen}",
                 lov=list_of_pollen_names,
                #  label="Pollen",
                 dropdown=True,
                 on_change=on_chang_pollen_selection,
                 )
    # tgb.table(data="{data_pollen}", page_size=10, height=400)
    tgb.chart(data="{data_pollen}",
              type="line",
              title="Concentration de pollen ",
              y="Concentration de pollen",
              x="time",
            xaxis={"title":"Time"},
            yaxis={"title":"Concentration de pollen (gr/m3)"},
            ymin=0,
            ymax=120,
              )


pages = {
    "/": root_page,
    "Sun_Flux": page_pollen,
}

if __name__ == "__main__":
    Gui(pages=pages,
        ).run(
        title="Dynamic chart",
        debug=True,
        use_reloader=True,
        )