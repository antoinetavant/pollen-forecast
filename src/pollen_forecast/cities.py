import pandas as pd
import logging
from pollen_forecast import ROOT_DIR

logger = logging.getLogger(__name__)

GEO_FILE = ROOT_DIR / "data" / "georef-france-commune.csv"

def load_city_list():
    print("Fetching list of cities")
    list_of_villes = pd.read_csv(GEO_FILE)
    print("List of cities fetched")
    availables_villes = list_of_villes["Nom Officiel Commune"].unique().tolist()
    print("List of cities transformed")
    return list_of_villes, sorted(availables_villes)

def closest_city_name(lat, lon, list_of_villes=None):
    """Returns the name of the closest city to the given coordinates"""
    if list_of_villes is None:
        list_of_villes, _ = load_city_list()

    distances = ((list_of_villes["latitude"] - lat) ** 2 + (list_of_villes["longitude"] - lon) ** 2) ** 0.5
    closest = distances.idxmin()
    commune = list_of_villes.loc[closest, "Nom Officiel Commune"]
    return commune