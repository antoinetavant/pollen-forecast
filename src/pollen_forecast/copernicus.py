import cdsapi
import xarray as xr
import pandas as pd
from pathlib import Path

class PollenForcastCopernicusGeneric:
    def __init__(self,
                 start="2024-05-26",
                 end=None,
                 model="ensemble",
                 variable="grass_pollen",
                 north=45.82,
                 south=45.67,
                 east=4.92,
                 west=4.66,
                 prefix=".",
                 leadtime_hour=None
                 ):
        self.c = cdsapi.Client()
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

        self.filename = Path(self.prefix + f"/{'_'.join(self.variable)}_{self.date_start}_{self.date_end}.nc")

    def get_pollen_data(self):

        self.c.retrieve(
            name=self.name,
            request=self.params,
            target=self.filename)
        return self.filename

    def pollen_data(self):
        ds = xr.open_dataset(self.filename)
        df = ds.mean(
            dim=["latitude", "longitude", "level"]
        ).to_dataframe()
        df.index += pd.Timestamp(self.date_start)
        return df