from pathlib import Path
from pollen_forecast.copernicus import PollenForcastCopernicusGeneric
from datetime import date
from cloudpathlib import S3Client
import dotenv
import os
import tqdm
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.info("Starting pollen data download")
dotenv.load_dotenv(".env.dev")
dates = [["2023-01-01", "2023-06-15"],
            ["2023-06-16", "2023-12-31"],
            ["2024-01-01", "2024-06-15"],
            ["2024-06-16", "2024-12-31"],
            ["2022-01-01", "2022-06-15"],
            ["2022-06-16", "2022-12-31"]]

# Use S3Path to access the data on S3
logger.info("Creating S3 client")

s3_client = S3Client(aws_access_key_id=os.environ["MINIO_ACCESS_KEY"],
                        aws_secret_access_key=os.environ["MINIO_SECRET_KEY"],
                        endpoint_url=os.environ["MINIO_URL"])

root_path = s3_client.CloudPath("s3://pollendata/")

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
