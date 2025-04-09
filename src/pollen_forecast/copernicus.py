import os
import cdsapi
import xarray as xr
import pandas as pd
from pathlib import Path
import logging
from cloudpathlib import CloudPath
logger = logging.getLogger(__name__)

class PollenForcastCopernicusGeneric:
    def __init__(
        self,
        start="2024-05-26",
        end=None,
        model="ensemble",
        variable="grass_pollen",
        north=45.82,
        south=45.67,
        east=4.92,
        west=4.66,
        prefix=Path.cwd(),
        leadtime_hour=None,
    ):
        self.c = cdsapi.Client(url=os.environ.get("CDSAPI_URL"), key=os.environ.get("CDSAPI_KEY"))
        self.name = "cams-europe-air-quality-forecasts"
        self.date_start = start
        self.date_end = end or start
        self.model = model
        if isinstance(variable, str):
            variable = [variable]
        elif not isinstance(variable, list):
            raise ValueError("variable must be a string or a list of strings")
        self.variable = variable
        self.north = north
        self.south = south
        self.east = east
        self.west = west
        self.leadtime_hour = leadtime_hour or [str(i) for i in range(0, 96)]
        self.level="0"
        self.prefix = prefix
        self.params = {
            "model": self.model,
            'variable': self.variable,
            'date': f'{self.date_start}/{self.date_end}',
            'format': 'netcdf',
            "level": self.level,
            "type": "forecast",
            "time": "00:00",
            "leadtime_hour": self.leadtime_hour,
            "area": [self.north, self.west, self.south, self.east],
        }
        self.ds = None

        try :
            self.filename = (
                self.prefix
                / f"{'_'.join(self.variable)}_{self.date_start}_{self.date_end}.nc"
            )
        except TypeError:
            self.prefix = Path(self.prefix)
            self.filename = (
                self.prefix
                / f"{'_'.join(self.variable)}_{self.date_start}_{self.date_end}.nc"
            )
        logger.debug(f"Filename set to {self.filename}")

    def get_pollen_data(self, check_exists=True):
        logger.debug("Ensuring the directory exists")
        self.filename.parent.mkdir(parents=True, exist_ok=True)
        logger.debug("Retrieving data from Copernicus")
        if check_exists and self.filename.exists():
            logger.debug(f"File {self.filename} already exists")
            return self.filename
        logger.debug("File does not exist, downloading data")
        need_upload = False
        if isinstance(self.filename, Path):
            target = str(self.filename)
        elif isinstance(self.filename, CloudPath):
            target = Path("/tmp/pollen_data")
            need_upload = True
        else: 
            raise ValueError("filename must be a Path or CloudPath")
        logger.debug(f"Target set to {target}")
        logger.debug(f"{self.params=}")
        self.c.retrieve(
            name=self.name,
            request=self.params,
            target=target)
        logger.debug("Data retrieved successfully")
        # Hot loading of the DataSet
        self.ds = xr.open_dataset(target, decode_timedelta=True)
        if need_upload:
            logger.debug("Uploading data to S3")
            self.filename.upload_from(target)
            logger.debug("Data uploaded successfully")
            target.unlink()
        return self.filename

    def pollen_data(self, latitude, longitude):
        if self.ds is None:
            logger.debug("Loading data from file")
            self.ds = xr.open_dataset(self.filename, decode_timedelta=True)
        self.ds.coords["longitude"] = (self.ds.coords["longitude"] + 180 ) % 360 - 180

        df = self.ds.sel(level=0,
                    latitude=latitude,
                    longitude=longitude,
                    method='nearest').to_dataframe()
        df.index += pd.Timestamp(self.date_start)
        return df
