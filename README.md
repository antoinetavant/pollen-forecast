# pollen-forecast

[![PyPI - Version](https://img.shields.io/pypi/v/pollen-forecast.svg)](https://pypi.org/project/pollen-forecast)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pollen-forecast.svg)](https://pypi.org/project/pollen-forecast)

-----

Pollen-Forecast is a tool to view the pollen forecast for a given location.
It uses the forecast data from the Copernicus Data Store (CDS) API.

Visualisation is done with HoloViz Pannel.

You can access the application at [antoinetavant.fr/app](https://antoinetavant.fr/app).

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Usage

You need a ECMWF account to access the data (see [Resources](#resources)).

Run the pollen forecast viewer with:

```console
hatch run prod:serve
```

## Resources

### CDS API

The Copernicus Data Store (CDS) API is used to retrieve the pollen forecast data.
The API requires an account to access the data.

The API is documented [here](https://ads.atmosphere.copernicus.eu/api-how-to).
Follow the instructions to create an account and get the API key.

The API key should be stored in a file named `.cdsapirc` in the user's home directory.


## License

`pollen-forecast` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
