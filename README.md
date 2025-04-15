# pollen-forecast

Pollen-Forecast is a tool to view the pollen forecast for a given location.
It uses the forecast data from the [Copernicus Data Store (CDS) API](https://ads.atmosphere.copernicus.eu/cdsapp#!/dataset/cams-europe-air-quality-forecasts?tab=overview).

The application is built using Django for the backend and provides a user-friendly interface for visualizing pollen forecasts.

You can access the application at [antoinetavant.fr/app](https://pollen.antoinetavant.fr).

## Usage

### Requirements
You need an ECMWF account to access the data (see [Resources](#resources)).

### Setup

1. Install the required dependencies:
   ```console
   pip install -r requirements.txt
   ```

2. Apply database migrations:
   ```console
   python src/pollen_forecast/djangoserver/manage.py migrate
   ```

3. Start the development server:
   ```console
   python src/pollen_forecast/djangoserver/manage.py runserver
   ```

4. Access the application at `http://127.0.0.1:8000`.

### Production Deployment

For production, use `uvicorn` to serve the application:
```console
uvicorn src.pollen_forecast.djangoserver.meteopollen.wsgi:application --host 0.0.0.0 --port 8000
```

## Resources

### Similar Projects

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
