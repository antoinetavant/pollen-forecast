# pollen-forecast

[![PyPI - Version](https://img.shields.io/pypi/v/pollen-forecast.svg)](https://pypi.org/project/pollen-forecast)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pollen-forecast.svg)](https://pypi.org/project/pollen-forecast)

-----

Pollen-Forecast is a tool to view the pollen forecast for a given location.
It uses the forecast data from the Copernicus Data Store (CDS) API.

Visualisation is done with NiceGui.

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install pollen-forecast
```

## Usage

Download the data using the Jupyter notebook `download_data.ipynb`.
You need a ECMWF account to access the data (see [Resources](#resources)).

Run the pollen forecast viewer with:

```console
python src/pollen_forecast/main.py
```

If you provide a NiceGui Token in a dotenv file, it will print the URL to open in your browser.

## TODO

- [ ] add a button to download the data
- [ ] compute averages for the historical data (5 or enven 10 years)
- [ ] improve layout

## Resources

### CDS API

The Copernicus Data Store (CDS) API is used to retrieve the pollen forecast data. The API requires an account to access the data. The API is documented [here](https://ads.atmosphere.copernicus.eu/api-how-to).


## License

`pollen-forecast` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
