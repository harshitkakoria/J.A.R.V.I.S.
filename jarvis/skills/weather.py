"""Weather information with dynamic city lookup."""
import requests

def handle(query: str) -> str:
    """Get weather info for any city."""
    if not any(kw in query.lower() for kw in ["weather", "temperature", "forecast", "rain", "hot", "cold"]):
        return None
    
    try:
        # Extract city from query
        q = query.lower()
        city = "Chennai"  # Default
        
        # Simple extraction: look for "in [city]" or "for [city]"
        for prep in [" in ", " for "]:
            if prep in q:
                city = q.split(prep, 1)[1].strip().split()[0].title()
                break
        
        # 1. Geocoding
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=en&format=json"
        geo_resp = requests.get(geo_url, timeout=5)
        geo_data = geo_resp.json()
        
        if not geo_data.get("results"):
            return f"I couldn't find the location '{city}'."
            
        location = geo_data["results"][0]
        lat = location["latitude"]
        lon = location["longitude"]
        place_name = location["name"]
        
        # 2. Weather
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,weather_code"
        resp = requests.get(url, timeout=5)
        
        if resp.status_code == 200:
            data = resp.json()["current"]
            temp = data["temperature_2m"]
            humid = data["relative_humidity_2m"]
            code = data["weather_code"]
            
            conditions = {0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 
                         51: "Drizzle", 53: "Drizzle", 55: "Drizzle",
                         61: "Rain", 63: "Rain", 65: "Heavy Rain", 
                         71: "Snow", 73: "Snow", 75: "Heavy Snow",
                         95: "Thunderstorm", 96: "Thunderstorm", 99: "Thunderstorm"}
            condition = conditions.get(code, "Unknown")
            
            return f"Weather in {place_name}: {temp}°C, {humid}% humidity, {condition}"
    except Exception as e:
        print(f"Weather error: {e}")
    
    return "Couldn't fetch weather right now."
