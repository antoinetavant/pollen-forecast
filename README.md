# pollen-forecast

[![PyPI - Version](https://img.shields.io/pypi/v/pollen-forecast.svg)](https://pypi.org/project/pollen-forecast)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pollen-forecast.svg)](https://pypi.org/project/pollen-forecast)

-----

Pollen-Forecast is a tool to view the pollen forecast for a given location.
It uses the forecast data from the [Copernicus Data Store (CDS) API](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-europe-air-quality-forecasts?tab=overview).

Visualisation is done with HoloViz Pannel.

You can access the application at [antoinetavant.fr/app](https://antoinetavant.fr/app).

## Usage

### Requirements
You need a ECMWF account to access the data (see [Resources](#resources)).

The project uses [hatch](https://hatch.pypa.io/latest/) to manage the environment and the dependencies.
You can install it with:

```console
pipx install hatch
```

### Launch the application

Run the pollen forecast viewer with:

```console
hatch run prod:serve
```

Or directly with:

```console
panel serve src/pollen_forecast/app.py
```


## Resources

### Similair projects

The Pollen forecast is available on the site [pollens.fr](https://www.pollens.fr/cartes-de-modelisations) but the temporal resolution is not as high as the one provided by the Copernicus Data Store.

The Copernicus website provides a [pollen forecast chart](https://atmosphere.copernicus.eu/charts/packages/cams_air_quality/products/europe-air-quality-forecast-pollens), but it is not as user-friendly as the one provided by this project.
Especially, the Copernicus website does not provide a way to select precisely a location on the map.

### CDS API

The Copernicus Data Store (CDS) API is used to retrieve the pollen forecast data.
The API requires an account to access the data.

The API is documented [here](https://ads.atmosphere.copernicus.eu/api-how-to).
Follow the instructions to create an account and get the API key.

The API key should be stored in a file named `.cdsapirc` in the user's home directory.


## License

`pollen-forecast` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
