from pathlib import Path
from pollen_forecast.copernicus import PollenForcastCopernicusGeneric
import datetime
from cloudpathlib import S3Client
import xarray as xr
import os
from tqdm import tqdm
import logging
import pandas as pd
from pollen_forecast.pollen import get_data_at_location, POLLEN_TRANSLATIONS, PollenForcastCopernicusGeneric, get_pollen_api
from cityforecast.tasks import load_pollen_data_for_prefectures

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def run():
    """Download pollen history data from the ACS, and upload it to the Data base"""
    logger.info("Starting pollen data download")
    load_pollen_data_for_prefectures()
