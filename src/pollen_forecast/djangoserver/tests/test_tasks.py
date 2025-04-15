from django.test import TestCase
from cityforecast.models import City, Pollen
from cityforecast.tasks import load_pollen_data_for_prefectures
from unittest.mock import patch
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class LoadPollenDataTest(TestCase):
    def setUp(self):
        # Create a mock prefecture city
        logger.info("start setting up cities")
        self.city = City.objects.create(
            official_city_name="Test City",
            official_department_name="Test Dep",
            latitude=45.75,
            longitude=4.85,
            is_prefecture=True,
        )

    @patch("cityforecast.tasks.get_data_at_location")
    def test_load_pollen_data_for_prefectures(self, mock_get_data_at_location):
        # Mock the return value of get_data_at_location
        logger.info("start test")
        mock_get_data_at_location.return_value = {
            "Aulne": pd.Series(
                [10, 20], index=["2025-03-20 00:00:00", "2025-03-20 01:00:00"]
            ),
            "Bouleau": pd.Series(
                [5, 15], index=["2025-03-20 00:00:00", "2025-03-20 01:00:00"]
            ),
        }

        # Run the task
        load_pollen_data_for_prefectures()

        # Check that Pollen objects were created
        self.assertEqual(PollenConcentrationForecasted.objects.count(), 4)

        # Verify the details of the created objects
        pollen = PollenConcentrationForecasted.objects.filter(
            cityname=self.city.official_city_name, pollen_type="Aulne"
        ).order_by("time")
        self.assertEqual(pollen[0].value, 10)
        self.assertEqual(pollen[1].value, 20)

        pollen = PollenConcentrationForecasted.objects.filter(
            cityname=self.city.official_city_name, pollen_type="Bouleau"
        ).order_by("time")
        self.assertEqual(pollen[0].value, 5)
        self.assertEqual(pollen[1].value, 15)
