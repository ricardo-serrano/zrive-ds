import requests

API_URL = "https://archive-api.open-meteo.com/v1/archive?"

COORDINATES = {
    "Madrid": {"latitude": 40.416775, "longitude": -3.703790},
    "London": {"latitude": 51.507351, "longitude": -0.127758},
    "Rio": {"latitude": -22.906847, "longitude": -43.172896},
}

TIMEZONES = {
    "Madrid": "Europe/Madrid"
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
                f"Failed to retrieve data for {city_name}. Status code: {response.status_code}"
            )
            return None

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def main():
    city_name = list(COORDINATES.keys())[0]
    latitude = COORDINATES[city_name]["latitude"]
    longitude = COORDINATES[city_name]["longitude"]

    city_data = get_data_meteo_api(
        api_url=API_URL,
        city_name=city_name,
        latitude=latitude,
        longitude=longitude,
        start_date=INITIAL_DATE,
        end_date=FINAL_DATE,
    )

    print(city_data)

    # raise NotImplementedError


if __name__ == "__main__":
    main()
