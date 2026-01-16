"""
Weather skill: Get weather information using free Open-Meteo API.
"""
from typing import Optional
from jarvis.utils.logger import setup_logger
from jarvis.settings import UserSettings

logger = setup_logger(__name__)


def handle(query: str) -> Optional[str]:
    """
    Handle weather queries.
    
    Args:
        query: User query about weather
        
    Returns:
        Weather information or None
    """
    try:
        import requests
        
        query_lower = query.lower()
        
        # Check if it's a weather query
        if not any(kw in query_lower for kw in ["weather", "temperature", "forecast", "rain", "cold", "hot", "climate", "humid"]):
            return None
        
        # Get user's city from settings
        settings = UserSettings.load()
        city = settings.city or "Chennai"
        
        # Get coordinates for the city (basic mapping)
        city_coords = {
            "delhi": (28.7041, 77.1025),
            "mumbai": (19.0760, 72.8777),
            "bangalore": (12.9716, 77.5946),
            "hyderabad": (17.3850, 78.4867),
            "kolkata": (22.5726, 88.3639),
            "chennai": (13.0827, 80.2707),
            "pune": (18.5204, 73.8567),
            "ahmedabad": (23.0225, 72.5714),
            "jaipur": (26.9124, 75.7873),
            "lucknow": (26.8467, 80.9462),
        }
        
        # Get coordinates (default to Chennai)
        coords = city_coords.get(city.lower(), (13.0827, 80.2707))
        latitude, longitude = coords
        
        # Query Open-Meteo API (free, no API key needed)
        url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            current = data.get("current", {})
            
            temp = current.get("temperature_2m", "N/A")
            humidity = current.get("relative_humidity_2m", "N/A")
            wind_speed = current.get("wind_speed_10m", "N/A")
            weather_code = current.get("weather_code", 0)
            
            # Convert weather code to description
            weather_desc = {
                0: "Clear sky",
                1: "Mainly clear",
                2: "Partly cloudy",
                3: "Overcast",
                45: "Foggy",
                48: "Foggy with rime",
                51: "Light drizzle",
                53: "Moderate drizzle",
                55: "Dense drizzle",
                61: "Slight rain",
                63: "Moderate rain",
                65: "Heavy rain",
                71: "Slight snow",
                73: "Moderate snow",
                75: "Heavy snow",
                80: "Slight rain showers",
                81: "Moderate rain showers",
                82: "Violent rain showers",
                85: "Slight snow showers",
                86: "Heavy snow showers",
                95: "Thunderstorm",
                96: "Thunderstorm with slight hail",
                99: "Thunderstorm with heavy hail",
            }
            
            description = weather_desc.get(weather_code, "Unknown")
            
            response_text = (
                f"Weather in {city}: {description}. "
                f"Temperature is {temp}°C with {humidity}% humidity and wind speed {wind_speed} km/h."
            )
            
            logger.info(f"Weather retrieved for {city}")
            return response_text
        else:
            logger.error(f"Weather API error: {response.status_code}")
            return f"Sorry, I couldn't fetch weather for {city}."
            
    except ImportError:
        logger.error("requests library not available")
        return "Weather library not installed."
    except Exception as e:
        logger.error(f"Weather error: {e}")
        return f"I encountered an error getting weather: {str(e)}"
