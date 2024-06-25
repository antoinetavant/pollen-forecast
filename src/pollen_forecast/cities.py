import logging
import pandas as pd
import difflib
import numpy as np
from pollen_forecast import ROOT_DIR

logger = logging.getLogger(__name__)

def load_city_list():
    logger.debug("Fetching list of cities")
    filename = ROOT_DIR / "notebooks" / "georef-france-commune.csv"
    list_of_villes = pd.read_csv(filename)
    list_of_villes_sorted = list_of_villes.sort_values("population", ascending=False)
    availables_villes = list_of_villes_sorted["Nom Officiel Commune"].tolist()
    return list_of_villes_sorted, availables_villes

def get_city_location(city_name):
    list_of_villes, _ = load_city_list()
    ville_line = list_of_villes[ list_of_villes["Nom Officiel Commune"] == city_name]
    latitude = ville_line["latitude"].values[0]
    longitude = ville_line["longitude"].values[0]
    return latitude, longitude

def search_closest_city(city_name):
    lists_of_cites, availables_villes = load_city_list()
    options = difflib.get_close_matches(city_name, availables_villes, n=10, cutoff=0.6)
    cities_selected = lists_of_cites[ lists_of_cites["Nom Officiel Commune"].isin(options)]
    n=4
    if len(cities_selected) > n:
        cities_selected = cities_selected.head(n)
    return cities_selected["Nom Officiel Commune"].tolist()

def find_closest_city(lat: float, lon: float)-> str:
    # closest city
    list_of_villes, _ = load_city_list()
    distances = np.sqrt((list_of_villes["latitude"] - lat)**2 + (list_of_villes["longitude"] - lon)**2)
    closest = distances.idxmin()
    commune = list_of_villes.loc[closest, "Nom Officiel Commune"]
    logger.info(f"Closest city: {commune}")
    return commune
