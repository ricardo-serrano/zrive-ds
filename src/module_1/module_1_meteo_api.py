import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

API_URL = "https://archive-api.open-meteo.com/v1/archive?"

COORDINATES = {
    "Madrid": {"latitude": 40.416775, "longitude": -3.703790},
    "London": {"latitude": 51.507351, "longitude": -0.127758},
    "Rio": {"latitude": -22.906847, "longitude": -43.172896},
}

INITIAL_DATE = "2010-01-01"

FINAL_DATE = "2020-12-31"

VARIABLES = ["temperature_2m_mean", "precipitation_sum", "wind_speed_10m_max"]


def get_data_meteo_api(api_url, city_name, latitude, longitude, start_date, end_date):
    """
    Calls the Open-Meteo API to retrieve weather data for a specific city.

    Args:
        api_url (str): The API url to connect.
        city_name (str): The name of the city.
        latitude (float): Latitude of the city.
        longitude (float): Longitude of the city.
        start_date (str): The start date for the data retrieval (YYYY-MM-DD).
        end_date (str): The end date for the data retrieval (YYYY-MM-DD).

    Returns:
        dict: The weather data for the city in JSON format if the request is successful.
    """
    # Define the API endpoint and query parameters

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "daily": VARIABLES,
    }

    try:
        # Send the request to the API
        response = requests.get(api_url, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            print(f"Data retrieved successfully for {city_name}")
            return response.json()  # Return the weather data in JSON format
        else:
            print(
                f"Failed to retrieve data for {city_name}. "
                f"Status code: {response.status_code}"
            )
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def transform_weather_data(api_response_json):
    """
    Transforms the weather data from the API response by extracting year and month,
    calculating the monthly mean, and pivoting the DataFrame for plotting.

    Args:
        api_response_json (dict): The JSON response from the Open-Meteo API containing
        the weather data.

    Returns:
        pd.DataFrame: A transformed DataFrame where the index is months, the columns are
         years and the values are temperature means.
        pd.DataFrame: A transformed DataFrame where the index is months, the columns are
         years and the values are precipitation sums.
        pd.DataFrame: A transformed DataFrame where the index is months, the columns are
         years and the values are wind speed maximums.
    """
    # Extract relevant data from the JSON response
    daily_data = api_response_json["daily"]

    # Create a DataFrame from the daily weather data
    df = pd.DataFrame(
        {
            "date": daily_data["time"],
            "temperature_2m_mean": daily_data["temperature_2m_mean"],
            "precipitation_sum": daily_data["precipitation_sum"],
            "wind_speed_10m_max": daily_data["wind_speed_10m_max"],
        }
    )

    # Convert 'date' column to datetime type
    df["date"] = pd.to_datetime(df["date"])

    # Extract year and month from the 'date' column
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month

    # Remove non-numeric columns before performing aggregation
    df_numeric = df.drop(columns=["date"])

    # Group by year and month and calculate the mean, sum, and max value for each month
    # and variable
    monthly_mean_data = df_numeric.groupby(["year", "month"]).mean().reset_index()
    monthly_sum_data = df_numeric.groupby(["year", "month"]).sum().reset_index()
    monthly_max_data = df_numeric.groupby(["year", "month"]).max().reset_index()

    # Pivot the DataFrame to have years as columns and months as rows for each variable
    temperature_pivot_table = monthly_mean_data.pivot(
        index="month", columns="year", values="temperature_2m_mean"
    )
    precipitation_pivot_table = monthly_sum_data.pivot(
        index="month", columns="year", values="precipitation_sum"
    )
    windspeed_pivot_table = monthly_max_data.pivot(
        index="month", columns="year", values="wind_speed_10m_max"
    )

    return temperature_pivot_table, precipitation_pivot_table, windspeed_pivot_table


def plot_variable(ax, data, title, ylabel, color_map):
    """
    Transforms the weather data from the API response by extracting year and month,
    calculating the monthly mean, and pivoting the DataFrame for plotting.

    Args:
        api_response_json (dict): The JSON response from the Open-Meteo API containing
        the weather data.

    Returns:
        pd.DataFrame: A transformed DataFrame where the index is months, the columns are
         years and the values are temperature means.
        pd.DataFrame: A transformed DataFrame where the index is months, the columns are
         years and the values are precipitation sums.
        pd.DataFrame: A transformed DataFrame where the index is months, the columns are
         years and the values are wind speed maximums.
    """
    years = sorted(data.columns)
    cmap = plt.get_cmap(color_map)
    norm = mcolors.Normalize(vmin=0, vmax=len(years) - 1)

    for i, year in enumerate(years):
        color = cmap(norm(i))
        ax.plot(data.index, data[year], label=f"{year}", color=color)

    # Customize the subplot
    ax.set_xlabel("Month")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.set_xticks(ticks=range(1, 13))
    ax.set_xticklabels(
        [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]
    )
    ax.grid(True)
    ax.legend(title="Year")


def plot_weather_data(
    temperature_pivot, precipitation_pivot, windspeed_pivot, city_name
):
    """
    Plots the weather data for temperature, precipitation, and wind speed simultaneously
    in subplots.
    Each year is plotted in a shade of a specific color, where earlier years are lighter
    and later years are darker.

    Args:
        temperature_pivot (pd.DataFrame): Pivot table of temperature data with months as
        index and years as columns.
        precipitation_pivot (pd.DataFrame): Pivot table of precipitation data with
        months as index and years as columns.
        windspeed_pivot (pd.DataFrame): Pivot table of wind speed data with months as
        index and years as columns.
        city_name (str): The name of the city to be used in the overall title.
    """
    # Create a figure with 3 subplots (1 row, 3 columns)
    fig, axs = plt.subplots(1, 3, figsize=(18, 6))

    # Plot temperature data with green shades in the first subplot
    plot_variable(
        axs[0],
        temperature_pivot,
        title="Mean Temperature (°C)",
        ylabel="Temperature (°C)",
        color_map="Greens",
    )

    # Plot precipitation data with blue shades in the second subplot
    plot_variable(
        axs[1],
        precipitation_pivot,
        title="Precipitation (mm)",
        ylabel="Precipitation (mm)",
        color_map="Blues",
    )

    # Plot wind speed data with red shades in the third subplot
    plot_variable(
        axs[2],
        windspeed_pivot,
        title="Max Wind Speed (km/h)",
        ylabel="Wind Speed (km/h)",
        color_map="Reds",
    )

    # Set the overall title for the figure using the city name
    fig.suptitle(f"Weather Data for {city_name}", fontsize=16)

    # Adjust layout to prevent overlap
    plt.tight_layout(rect=[0, 0, 1, 0.95])

    # Show the plot
    plt.show()


def main():
    # Iterate over each city in the COORDINATES dictionary
    for city_name, coords in COORDINATES.items():
        print(f"Processing data for {city_name}...")

        # Step 1: Get the data from the meteo API for each city
        latitude = coords["latitude"]
        longitude = coords["longitude"]

        city_data = get_data_meteo_api(
            api_url=API_URL,
            city_name=city_name,
            latitude=latitude,
            longitude=longitude,
            start_date=INITIAL_DATE,
            end_date=FINAL_DATE,
        )

        if city_data is None:
            print(f"Skipping {city_name} due to data retrieval issues.")
            continue  # Skip to the next city if data retrieval fails

        # Step 2: Transform the data from the API response
        (
            temperature_pivot,
            precipitation_pivot,
            windspeed_pivot,
        ) = transform_weather_data(city_data)

        # Step 3: Plot the transformed data
        plot_weather_data(
            temperature_pivot, precipitation_pivot, windspeed_pivot, city_name
        )

        print(f"Finished processing {city_name}\n")


if __name__ == "__main__":
    main()
