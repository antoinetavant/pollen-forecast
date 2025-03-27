"""Define here the tasks, like daily jobs"""
from datetime import date

from tqdm import tqdm
from cityforecast.models import City, PollenConcentrationForecasted
from pollen_forecast.pollen import get_data_at_location, POLLEN_TRANSLATIONS

def load_pollen_data_for_prefectures(batch_size=100):
    """Load pollen data for each prefecture city into the Pollen model using batching."""
    today = date.today()
    prefecture_cities = City.objects.filter(is_prefecture=True)
    for city in tqdm(prefecture_cities):
        try:
            load_pollen_data_fore_one_city(today, city, batch_size)
        except Exception as e:
            # Log the error for debugging
            print(f"Error loading pollen data for {city.official_city_name}: {e}")


def load_pollen_data_fore_one_city(today, city, batch_size=100):
    pollen_data = get_data_at_location(
        date=today, latitude=city.latitude, longitude=city.longitude
    )[POLLEN_TRANSLATIONS.values()]
    pollen_data.index = pollen_data.index.tz_localize("UTC")

    # print(pollen_data)
    pollen_objects = []  # Collect objects to be created in bulk
    for pollen_type, series in pollen_data.items():
        for index, val in series.items():
            pollen_objects.append(
                PollenConcentrationForecasted(
                    city=city,  # Use city as a foreign key
                    forecasted_at=today,
                    pollen_type=pollen_type,
                    time=index,
                    value=val,
                )
            )
            # Bulk create objects in batches
    for i in range(0, len(pollen_objects), batch_size):
        PollenConcentrationForecasted.objects.bulk_create(
            pollen_objects[i : i + batch_size]
        )

