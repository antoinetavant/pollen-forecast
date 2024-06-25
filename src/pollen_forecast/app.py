import streamlit as st
import pandas as pd
from pollen_forecast.pollen import get_data_at_location, list_of_pollen_names
from pollen_forecast.cities import get_city_location, search_closest_city, find_closest_city
import altair as alt
from streamlit_searchbox import st_searchbox
from streamlit_geolocation import streamlit_geolocation

st.set_page_config(initial_sidebar_state="collapsed",
                   page_title="Météo pollen",
                   page_icon="🤧",
                #    layout="wide",

                   )
st.title("Prévision du pollen")


st.sidebar.title("Options")
st.sidebar.markdown("Sélectionnez la date a laquelle vous voulez voir la prévision du pollen.")
today = (pd.Timestamp("today") - pd.DateOffset(hours=8)  ).date()
today = st.sidebar.date_input("Date",
                      value=today,
                      min_value=None,
                      max_value=today,
                      key=None)

left_column, right_column = st.columns(2)

with left_column:
    city_name = st_searchbox(search_closest_city,
                             label="Nom de la ville",
                             default="Lyon",
                             rerun_on_update=False
                             )
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

polen_type = right_column.selectbox("Type de pollen",
                                    list_of_pollen_names,
                                    index= list_of_pollen_names.index("Graminées"))

st.markdown(f"Prévision du pollen pour {city_name} le {today}")

my_barplot = alt.Chart(data.reset_index()).mark_bar().encode(
    y=polen_type,
    x="time"

)
st.altair_chart(my_barplot,
                use_container_width=True
             )