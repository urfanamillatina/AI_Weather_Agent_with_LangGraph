"""
weather_tool.py
----------------
A simple utility module that queries OpenWeatherMap for current weather.

Functions
---------
get_weather(city: str) -> dict | None
    Calls the OpenWeatherMap "current weather" endpoint and returns a dict with
    normalized fields (city, description, temp_c, humidity, wind). Returns None
    if the API responds with a non-200 "cod".

format_weather_text(w: dict | None) -> str
    Converts the normalized weather dict into a single readable sentence.

Notes
-----
• This module is intentionally small so it can serve as a "tool" node inside LangGraph.
• We separate API access (this file) from the graph logic (agent_graph.py).
"""
import os
import requests

def get_weather(city: str):
    """Fetch current weather for a city from OpenWeatherMap. Return normalized dict or None."""
    key = os.getenv("WEATHER_API_KEY")
    if not key:
        raise RuntimeError("WEATHER_API_KEY missing in environment")
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": key, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    data = r.json()
    # OpenWeatherMap uses 'cod' to indicate status; it can be int or str
    if str(data.get("cod")) != "200":
        return None
    return {
        "city": city.title(),
        "description": data["weather"][0]["description"],
        "temp_c": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind": data.get("wind", {}).get("speed", None)
    }

def format_weather_text(w):
    """Turn the weather dict into a readable summary string."""
    if not w:
        return "No weather data."
    parts = [
        f"The weather in {w['city']} is {w['description']}.",
        f"Temperature: {w['temp_c']}°C.",
        f"Humidity: {w['humidity']}%."
    ]
    if w.get("wind") is not None:
        parts.append(f"Wind: {w['wind']} m/s.")
    return " ".join(parts)
