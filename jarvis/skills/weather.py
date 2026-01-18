"""Weather information."""
import requests


def handle(query: str) -> str:
    """Get weather info."""
    if not any(kw in query.lower() for kw in ["weather", "temperature", "forecast", "rain", "hot", "cold"]):
        return None
    
    try:
        # Default city
        city = "Chennai"
        coords = {"chennai": (13.0827, 80.2707), "delhi": (28.7041, 77.1025), 
                  "mumbai": (19.0760, 72.8777), "bangalore": (12.9716, 77.5946)}
        
        lat, lon = coords.get(city.lower(), (13.0827, 80.2707))
        
        # Free API
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code"
        resp = requests.get(url, timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()["current"]
            temp = data["temperature_2m"]
            humid = data["relative_humidity_2m"]
            code = data["weather_code"]
            
            conditions = {0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 
                         51: "Drizzle", 61: "Rain", 71: "Snow", 95: "Thunderstorm"}
            condition = conditions.get(code, "Unknown")
            
            return f"Weather in {city}: {temp}°C, {humid}% humidity, {condition}"
    except:
        pass
    
    return "Couldn't fetch weather"
