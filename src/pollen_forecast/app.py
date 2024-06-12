"""Uses Holoviz panel to create a web app for the pollen forecast model."""

import hvplot.pandas
import numpy as np
import pandas as pd
import panel as pn
from bokeh.models.formatters import DatetimeTickFormatter
from pollen_forecast.copernicus import PollenForcastCopernicusGeneric
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

PRIMARY_COLOR = "#0072B5"
SECONDARY_COLOR = "#B54300"

pn.extension(
             design="bootstrap",
             sizing_mode="stretch_width",
             loading_spinner='dots',
             loading_color='#00aa41',
             )
impage_flower = pn.pane.JPG("https://upload.wikimedia.org/wikipedia/commons/4/47/Pollen_from_Dactylis_glomerata.jpg")

template = pn.template.BootstrapTemplate(
    title="Prévision du pollen",
    sidebar=[impage_flower, "Visualisation de la prévision du pollen pour une ville donnée."],
    main=[],
    header_background=PRIMARY_COLOR,
    sidebar_width=300,
    main_max_width="1000px",
    collapsed_sidebar=True,
    modal=["Autorisez la géolocalisation pour obtenir la prévision du pollen pour votre ville."]
)



# Define the translations for the pollen variables
POLLEN_TRANSLATIONS = {
    "apg_conc": "Aulne",  #"Alder Pollen",
    "bpg_conc": "Bouleau",  #"Birch Pollen",
    "gpg_conc": "Graminées",  #"Grass Pollen",
    "mpg_conc": "Armoise",  #"Mugwort Pollen",
    "opg_conc": "Olive", #"Olive Pollen",
    "rwpg_conc": "Ambroisie", #"Ragweed Pollen",
}

def get_data(date=(pd.Timestamp("today") - pd.Timedelta("8h")).date(),
             latitude= 45.75,
             longitude= 4.85):
    print("Fetching data")
    my_api = fetch_pollen_data(date)
    print(f"{latitude=}, {longitude=}")
    return my_api.pollen_data(latitude=latitude, longitude=longitude).rename(columns=POLLEN_TRANSLATIONS)

@pn.cache
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
        print("Downloading data")
        my_api.get_pollen_data()
    return my_api


def transform_data(data, variable, normalization=False):
    """Calculates the rolling average and identifies outliers"""
    selection = data[variable]
    if normalization:
        for col in selection.columns:
            selection[col] = selection[col] / selection[col].max()
    return selection



def load_city_list():
    print("Fetching list of cities")
    list_of_villes = pd.read_csv("georef-france-commune.csv")
    print("List of cities fetched")
    availables_villes = list_of_villes["Nom Officiel Commune"].unique().tolist()
    print("List of cities transformed")
    return list_of_villes, sorted(availables_villes)

list_of_villes, availables_villes = load_city_list()
# champs de recherche pour villes
ville_widget = pn.widgets.AutocompleteInput(
    name="Ville",
    options=availables_villes,
    placeholder="Entrez une ville",
    case_sensitive=False,
    search_strategy='includes',
    restrict=True,
)
logger.info("Ville widget created")

variable_widget = pn.widgets.RadioBoxGroup(
    name="variable", value="Graminées", options=list(POLLEN_TRANSLATIONS.values()), inline=True
)
def get_plot(variable="Graminées",
             commune="Lyon",
             ):
    """Plots the rolling average and the outliers"""
    print(f"{commune=}")
    if commune == "":
        commune = "Lyon"
    ville_line = list_of_villes[ list_of_villes["Nom Officiel Commune"] == commune]
    latitude = ville_line["latitude"].values[0]
    longitude = ville_line["longitude"].values[0]
    data = get_data(latitude=latitude, longitude=longitude)
    avg = transform_data(data, variable, normalization=False)
    # add title the commune name
    avg = avg.hvplot(height=300, legend=False, color=PRIMARY_COLOR)
    # one tick every 3 hours
    formatter = DatetimeTickFormatter(hours="%H:%M",
                                      days="%a %d %b",
                                      months="%m/%Y",
                                      years="%Y")


    avg.opts(title=f"Prévision du pollen à {commune}",
                xlabel="Date",
                ylabel="Concentration de pollen",
                xformatter=formatter,

                )

    return avg


bound_plot = pn.param.ParamFunction(
    pn.bind(get_plot, variable=variable_widget, commune=ville_widget),
    loading_indicator=True,
)

# Create a TextInput to hold latitude and longitude
# do not show it to the user with
lat_input = pn.widgets.FloatInput(name='Latitude', placeholder='Latitude',
                                  disabled=True,
                                  visible=False,
                                  )
lon_input = pn.widgets.FloatInput(name='Longitude',
                                  placeholder='Longitude',
                                  disabled=True,
                                  visible=False,
                                  )

# JavaScript code to fetch user location
js_code = """
lat_input.value = -777;
lon_input.value = -777;
setTimeout(function() {

navigator.geolocation.getCurrentPosition(
    function(position) {
        lat_input.value = position.coords.latitude;
        lon_input.value = position.coords.longitude;
    },
    function(error) {
        lat_input.value = -999;
        lon_input.value = -999;
    },
    {timeout: 10000,
    maximumAge: 60000
    });
    }, 100);
"""

get_location_button = pn.widgets.Button(name='⌖', width=50, description="Utiliser ma position")
get_location_button.js_on_click(args={'lat_input': lat_input, 'lon_input': lon_input}, code=js_code)

def start_loading(event):
    app.loading = True
    get_location_button.disabled = True

def stop_loading():
    app.loading = False
    get_location_button.disabled = False

get_location_button.on_click(start_loading)

@pn.depends(lat_input, lon_input, watch=True)
def handle_location_event(lat, lon):
    # closest city
    logger.info(f"Latitude: {lat}, Longitude: {lon}")
    if lat == -999 or lon == -999:
        stop_loading()
        template.open_modal()
        lat_input.value = -777
        lon_input.value = -777
        return
    if lat == -777 or lon == -777:
        return
    distances = np.sqrt((list_of_villes["latitude"] - lat)**2 + (list_of_villes["longitude"] - lon)**2)
    closest = distances.idxmin()
    commune = list_of_villes.loc[closest, "Nom Officiel Commune"]
    logger.info(f"Closest city: {commune}")
    ville_widget.value = commune
    ville_widget.param.trigger("value")
    stop_loading()



app = pn.Column(
    pn.pane.Markdown(
        """
        # Prévision du pollen

        Ce graphique montre la prévision du pollen pour une ville donnée.
        """
    ),

    pn.Row(variable_widget, ville_widget, get_location_button),
    bound_plot,

    lat_input,
    lon_input,
)

footer_text = pn.pane.Markdown(
    """
    Ce graphique est basé sur les données de [Copernicus](https://www.copernicus.eu/en).
    Elles sont mises à jour tous les jours à 8h UTC.

    Le code source est disponible sur [GitHub](https://github.com/antoinetavant/pollen-forecast).
    """
)

template.main.append(app)
template.main.append(footer_text)


template.servable()
