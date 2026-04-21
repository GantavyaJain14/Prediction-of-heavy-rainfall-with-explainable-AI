import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_current_weather(city="London"):
    """
    Fetches current weather data for a specified city using OpenWeatherMap API.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise ValueError("No API key found. Please set OPENWEATHER_API_KEY in .env file.")

    base_url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric" # Use metric units for Celsius
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() # Raise exception for 4xx/5xx errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_forecast(city="London"):
    """
    Fetches 5-day/3-hour forecast data for nowcasting.
    """
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return None

    base_url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "cnt": 3  # Get next 3 data points (approx next 9 hours)
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching forecast data: {e}")
        return None

if __name__ == "__main__":
    # Example usage
    city = "London"
    print(f"Fetching weather for {city}...")
    weather_data = get_current_weather(city)
    
    if weather_data:
        print(f"Successfully fetched data for {city}!")
        print(f"Temperature: {weather_data['main']['temp']}°C")
        print(f"Weather: {weather_data['weather'][0]['description']}")
    else:
        print("Failed to fetch weather data.")
