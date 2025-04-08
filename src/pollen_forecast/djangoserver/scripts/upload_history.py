from pathlib import Path
from pollen_forecast.copernicus import PollenForcastCopernicusGeneric
from datetime import date
from cloudpathlib import S3Client
import xarray as xr
import os
import tqdm
import logging
import pandas as pd
from pollen_forecast.pollen import POLLEN_TRANSLATIONS
from cityforecast.models import PollenConcentrationHistory

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def open_one_file(filename, start_date):
    """Load one file, and return the average over the square Inscrit."""
    lon_min = -1
    lon_max = 6
    lat_min = 43.5
    lat_max = 49.2
    ds = xr.open_dataset(filename, engine="netcdf4")
    ds.coords["longitude"] = (ds.coords["longitude"] + 180 ) % 360 - 180
    df = ds.sel(level=0).sel(
            latitude=slice(lat_max, lat_min),
            longitude=slice(lon_min, lon_max)
    ).mean(dim=["latitude", "longitude"]).to_dataframe()
    df.index += start_date
    return df
    
def run():
    """Download pollen history data from the ACS, and upload it to the Data base"""
    logger.info("Starting pollen data download")
    dates = [["2023-01-01", "2023-06-15"],
            ["2023-06-16", "2023-12-31"],
            ["2024-01-01", "2024-06-15"],
            ["2024-06-16", "2024-12-31"],
            ["2022-01-01", "2022-06-15"],
            ["2022-06-16", "2022-12-31"]]

        
    s3_client = S3Client(aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
                            aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
                            endpoint_url=os.environ["MINIO_URL"])

    root_path = s3_client.CloudPath("s3://pollendata/")

    pollens = []
    for start_date, end_date in tqdm.tqdm(dates):
        logger.info(f"Downloading pollen data from {start_date} to {end_date}")
        my_api = PollenForcastCopernicusGeneric(
                start=start_date,
                end=end_date,
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
                prefix=root_path,
                leadtime_hour=[str(i) for i in range(0, 23,6)],
            )

        filename = my_api.get_pollen_data()

        df = open_one_file(filename, pd.to_datetime(start_date, utc=True)).drop(columns=["level"]).resample("1D").mean().fillna(0)
        
        logger.info(f"Data shape: {df.shape}")
        logger.info(f"Data columns: {df.columns}")
        logger.info(f"Data Summary: {df.describe()}")
        
        logger.info("Starting uploading to Django Model")
        for pollen_type, series in df.items():
            for index, val in series.items():
                pollens.append(
                    PollenConcentrationHistory(
                        time=index,
                        pollen_type=POLLEN_TRANSLATIONS[pollen_type],
                        value=val,
                    )
                )
        PollenConcentrationHistory.objects.bulk_create(pollens, batch_size=1000, ignore_conflicts=True)
        logger.info("Upload finished")
    