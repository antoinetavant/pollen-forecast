from pathlib import Path
from pollen_forecast.copernicus import PollenForcastCopernicusGeneric
import pandas as pd
import logging

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

# Define levels and categories
levels_graminees = [0, 4, 19, 50, 100, 9999]
levels_herbes = [0, 9, 50, 100, 250, 9999]
levels_arbres = [0, 15, 90, 250, 1500, 9999]
level_names = ["faible", "moderé", "modéré-fort", "fort", "très fort"]
list_herbes = ["Ambroisie", "Armoise"]
list_arbes = ["Aulne", "Bouleau", "Olive"]
list_graminees = ["Graminées"]
plant_types = {
    "Ambroisie": "herbes",
    "Armoise": "herbes",
    "Aulne": "arbres",
    "Bouleau": "arbres",
    "Olive": "arbres",
    "Graminées": "graminées",
}
levels_map = {
    "arbres": levels_arbres,
    "herbes": levels_herbes,
    "graminées": levels_graminees,
}

def get_pollen_api(date, prefix=Path("./france_territory/")) -> PollenForcastCopernicusGeneric:
    """Init the PollenForcastCopernicusGeneric object and download the data if needed.

    Parameters
    ----------
    date: pd.Timestamp
        The date for which the data is needed.

    Returns
    -------
    PollenForcastCopernicusGeneric
        The PollenForcastCopernicusGeneric object with the data.

    """
    if isinstance(date, pd.Timestamp):
        date = date.strftime("%Y-%m-%d")
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
        prefix=prefix,
    )
    if not my_api.filename.exists():
        logger.debug("Downloading Copernicus data")
        my_api.get_pollen_data()
    return my_api


def get_data_at_location(
    date=(pd.Timestamp("today") - pd.Timedelta("8h")).date(),
    latitude=45.75,
    longitude=4.85,
    pollen_api=None,
    prefix=Path("./france_territory/")  # Default prefix
):
    """Return a DataFrom with the pollen data for the given date and location.
    Columns are renamed using the POLLEN_TRANSLATIONS dictionary.
    """
    logger.debug("Fetching data")
    my_api = pollen_api or get_pollen_api(date, prefix=prefix)
    logger.debug(f"{latitude=}, {longitude=}")
    return my_api.pollen_data(latitude=latitude, longitude=longitude).rename(columns=POLLEN_TRANSLATIONS)
