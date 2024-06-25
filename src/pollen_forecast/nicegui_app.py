import os
from nicegui import ui
import pandas as pd
import xarray as xr
import dotenv

dotenv.load_dotenv()
filename_2023 = "./2023_previsions.nc"
filename_2024 = "./today_previsions.nc"

ds_2023 = xr.open_dataset(filename_2023)
mean_gpg_2023 = ds_2023.mean(
    dim=["latitude", "longitude", "level"]
).gpg_conc.to_dataframe()
start_date = "2023-03-01"
mean_gpg_2023.index += pd.Timestamp(start_date)
ds_2024 = xr.open_dataset(filename_2024)
mean_gpg_2024 = ds_2024.mean(
    dim=["latitude", "longitude", "level"]
).gpg_conc.to_dataframe()
mean_gpg_2024.index += pd.Timestamp("today").floor("D")
mean_gpg_2024_in_2023 = mean_gpg_2024.copy()
mean_gpg_2024_in_2023.index = mean_gpg_2024.index - pd.DateOffset(years=1)


# Convert DataFrame to list of dictionaries
pollen_data_2023 = mean_gpg_2023.reset_index().to_dict(orient="records")
pollen_data_2024 = mean_gpg_2024_in_2023.reset_index().to_dict(orient="records")

# convert the Timestamp to string with hours
format = "%Y-%m-%d %H:%M:%S"
for record in pollen_data_2023:
    record["time"] = record["time"].strftime(format)
    # round the value
    record["gpg_conc"] = round(record["gpg_conc"], 2)
for record in pollen_data_2024:
    record["time"] = record["time"].strftime(format)
    record["gpg_conc"] = round(record["gpg_conc"], 2)

# convert the dictionary to a list of lists
pollen_data_2023 = [[record["time"], record["gpg_conc"]] for record in pollen_data_2023]
pollen_data_2024 = [[record["time"], record["gpg_conc"]] for record in pollen_data_2024]


plot = ui.echart({
    "title": {"text": "Grass Pollen Forecast"},
    "xAxis": {"type": "time"},
    "yAxis": {"type": "value"},
    "series": [
        {"name": "2023",
         "type": "line",
         "data": pollen_data_2023},
        {"name": "2024",
         "type": "line",
         "data": pollen_data_2024},
    ],
    # add tooltip with format for floating numbers
    "tooltip": {"trigger": "axis",
                },
    # add zoom
    "dataZoom": [
        {"type": "inside"},
        {"type": "slider"},
    ],
    "legend": {
        "data": ["2023", "2024"]
    },


})

# add a button to switch to daily averages
def daily_averages():
    # calculate daily averages
    daily_averages_2023 = mean_gpg_2023.resample("D").mean()
    daily_averages_2024 = mean_gpg_2024_in_2023.resample("D").mean()
    # convert the DataFrame to a list of dictionaries
    daily_averages_2023 = daily_averages_2023.reset_index().to_dict(orient="records")
    daily_averages_2024 = daily_averages_2024.reset_index().to_dict(orient="records")
    # convert the Timestamp to string
    format = "%Y-%m-%d"
    for record in daily_averages_2023:
        record["time"] = record["time"].strftime(format)
        record["gpg_conc"] = round(record["gpg_conc"], 2)
    for record in daily_averages_2024:
        record["time"] = record["time"].strftime(format)
        record["gpg_conc"] = round(record["gpg_conc"], 2)
    # convert the dictionary to a list of lists
    daily_averages_2023 = [[record["time"], record["gpg_conc"]] for record in daily_averages_2023]
    daily_averages_2024 = [[record["time"], record["gpg_conc"]] for record in daily_averages_2024]
    # update the plot
    plot.options["series"][0]["data"] = daily_averages_2023
    plot.options["series"][1]["data"] = daily_averages_2024
    plot.update()

#switch to hourly data
def hourly_data():
    plot.options["series"][0]["data"] = pollen_data_2023
    plot.options["series"][1]["data"] = pollen_data_2024
    plot.update()

ui.button("Daily averages", on_click=daily_averages)
ui.button("Hourly data", on_click=hourly_data)

# add button to focus the zoom on today
def focus_today():
    today = pd.Timestamp("today").date()
    today_in_2023 = today.replace(year=2023)
    tomorrow_in_2023 = today_in_2023 + pd.DateOffset(days=2)
    plot.run_chart_method("dispatchAction", {"type": "dataZoom", "startValue": today_in_2023.strftime(format), "endValue": tomorrow_in_2023.strftime(format)})

# add button to focus the zoom on today
ui.button("Focus on today", on_click=focus_today)

# add table of today average value, and the same day in 2023
today = pd.Timestamp("today").date()
today_in_2023 = today.replace(year=2023)
next_day_in_2023 = today_in_2023 + pd.DateOffset(days=1)

today_average_2023 = mean_gpg_2023.loc[today_in_2023: next_day_in_2023].mean().item()
today_average_2024 = mean_gpg_2024_in_2023.loc[today_in_2023: next_day_in_2023].mean().item()

format_day = "%Y-%m-%d"
ui.table(columns=[
    {"name": "Year", "label": "Year", "field": "year"},
    {"name": "Date", "label": "Date", "field": "date"},
    {"name": "Average", "label": "Average (gains/m^3)", "field": "average"}
],
            rows=[{"year": "2023", "date": today_in_2023.strftime(format_day), "average": round(today_average_2023, 2)},
                {"year": "2024", "date": today.strftime(format_day), "average": round(today_average_2024, 2)},
])


token = os.getenv("NICEGUI_TOKEN")

print(token)
ui.run(on_air=token)