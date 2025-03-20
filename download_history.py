import cdsapi

dataset = "cams-europe-air-quality-forecasts"
request = {
    "variable": [
        "alder_pollen",
        "birch_pollen",
        "grass_pollen",
        "mugwort_pollen",
        "olive_pollen",
        "ragweed_pollen",
    ],
    "model": ["ensemble"],
    "level": ["0"],
    "date": ["2023-06-16/2023-12-31"],
    "type": ["forecast"],
    "time": ["00:00"],
    "leadtime_hour": ["0", "6", "12", "18"],
    "data_format": "netcdf_zip",
    "area": [51.7, -5.33, 41.87, 8.74],
}

client = cdsapi.Client()
client.retrieve(dataset, request).download()
