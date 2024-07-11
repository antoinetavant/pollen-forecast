import altair as alt
import pandas as pd
import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from streamlit_searchbox import st_searchbox

from pollen_forecast.cities import (
    find_closest_city,
    get_city_location,
    search_closest_city,
)
from pollen_forecast.pollen import get_data_at_location, list_of_pollen_names

st.set_page_config(
    initial_sidebar_state="collapsed",
    page_title="Météo pollen",
    page_icon="🤧",
    #    layout="wide",
)
st.title("Prévision du pollen")


st.sidebar.title("Options")
st.sidebar.markdown(
    "Sélectionnez la date a laquelle vous voulez voir la prévision du pollen."
)
today = (pd.Timestamp("today") - pd.DateOffset(hours=8)).date()
today = st.sidebar.date_input(
    "Date", value=today, min_value=None, max_value=today, key=None
)

left_column, midle_column, right_column = st.columns(3)

with left_column:
    city_name = st_searchbox(
        search_closest_city,
        label="Nom de la ville",
        default="Lyon",
        rerun_on_update=False,
    )
with midle_column:
    st.write("utiliser ma position actuelle")
    location = streamlit_geolocation()


@st.cache_data
def get_city_location_cached(city_name):
    return get_city_location(city_name)


def get_lat_lon(city_name: str):
    if location["latitude"]:
        print(location)
        city_name = find_closest_city(location["latitude"], location["longitude"])
        return location["latitude"], location["longitude"], city_name
    else:
        return *get_city_location_cached(city_name), city_name


lat, lon, city_name = get_lat_lon(city_name)


@st.cache_data
def get_data_at_location_cached(today, lat, lon):
    return get_data_at_location(today, lat, lon)


data = get_data_at_location_cached(today, lat, lon)
levels_graminees = [0, 4, 19, 50, 100, 9999]
levels_herbes = [0, 9, 50, 100, 250, 9999]
levels_arbres = [0, 15, 90, 250, 1500, 9999]
level_names = ["faible", "moderé", "modéré-fort", "fort", "très fort"]
list_herbes = ["Ambroisie", "Armoise"]
list_arbes = ["Aulne", "Bouleau", "Olive"]
list_graminees = ["Graminées"]

for list_pollen, levels in zip(
    [list_herbes, list_arbes, list_graminees],
    [levels_herbes, levels_arbres, levels_graminees],
):
    for pollen in list_pollen:
        niveau_name = f"{pollen}_niveau"
        data[niveau_name] = pd.cut(data[pollen], levels, labels=level_names)

polen_type = right_column.selectbox(
    "Type de pollen",
    list_of_pollen_names,
    index=list_of_pollen_names.index("Graminées"),
)

st.markdown(f"Prévision du pollen pour {city_name} le {today}")

my_barplot = (
    alt.Chart(data.reset_index())
    .mark_bar()
    .encode(
        y=polen_type,
        x=alt.X("time", title="Date"),
        color=alt.Color(
            f"{polen_type}_niveau",
            scale=alt.Scale(
                domain=level_names, range=["green", "gold", "orange", "red", "purple"]
            ),
            title="Niveau de risque",
        ),
    )
)
st.altair_chart(my_barplot, use_container_width=True)
