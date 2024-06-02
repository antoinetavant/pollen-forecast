# pollen-forecast

[![PyPI - Version](https://img.shields.io/pypi/v/pollen-forecast.svg)](https://pypi.org/project/pollen-forecast)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pollen-forecast.svg)](https://pypi.org/project/pollen-forecast)

-----

Pollen-Forecast is a tool to view the pollen forecast for a given location.
It uses the forecast data from the Copernicus Data Store (CDS) API.

Visualisation is done with HoloViz Pannel.

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install pollen-forecast
```

## Usage

You need a ECMWF account to access the data (see [Resources](#resources)).

Run the pollen forecast viewer with:

```console
panel serve src/pollen_forecast/app.py
```

## TODO

- [ ] add a button to download the data
- [ ] compute averages for the historical data (5 or enven 10 years)
- [ ] improve layout

## Resources

### CDS API

The Copernicus Data Store (CDS) API is used to retrieve the pollen forecast data.
The API requires an account to access the data.

The API is documented [here](https://ads.atmosphere.copernicus.eu/api-how-to).
Follow the instructions to create an account and get the API key.

The API key should be stored in a file named `.cdsapirc` in the user's home directory.


## License

`pollen-forecast` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
