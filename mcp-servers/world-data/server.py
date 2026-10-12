# loading libraries
import os
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

#Loading environment variables
load_dotenv()

# Creating MCP server
mcp = FastMCP("World Data Server")

# Handling error related to API key
@mcp.tool
def search_news(query: str) -> dict:
    api_key = os.getenv("NEWSAPI_API_KEY")
    if not api_key:
        return {"error": "NEWSAPI_KEY not set in environment"}

   # Preparing parametr
    params = {
        "q": query,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 1,
        "apiKey": api_key
    }

    # Calling API
    NEWS_API_URL = "https://newsapi.org/v2/everything"
    response = requests.get(NEWS_API_URL, params=params, timeout=10)

    # Handling errors
    if response.status_code != 200:
        return {
            "error": "NewsAPI request failed",
            "status_code": response.status_code,
            "details": response.text
        }

    data = response.json()
    articles = data.get("articles", [])

    if not articles:
        return {"query": query, "articles": []}

    # Using first article in repose
    article = articles[0]
    return {
        "query": query,
        "headline": article.get("title"),
        "description": article.get("description"),
        "source": article.get("source", {}).get("name"),
        "url": article.get("url"),
        "published_at": article.get("publishedAt")
    }
    
    
    
# Function to get weather data for a given city
@mcp.tool
def get_weather(city: str, units: str = "metric") -> dict:
    
    # handling weather api
    weather_api_key = os.getenv("OPENWEATHER_API_KEY")
    if not weather_api_key:
        return {"error": "OPENWEATHER_API_KEY not set in environment"}
    
    # Preparing parameters
    params = {"q": city, "appid": weather_api_key, "units": units}

    # Calling API and handling different responses
    OPENWEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"
    try:
        response = requests.get(OPENWEATHER_API_URL, params=params, timeout=10)

        if response.status_code == 404:
            return {"error": f"City '{city}' not found."}
        elif response.status_code == 401:
            return {"error": "Invalid API Key."}

        response.raise_for_status()
        data = response.json()

        # Returing reposne
        return {
            "city": data.get("name"),
            "country": data.get("sys", {}).get("country"),
            "temperature": data.get("main", {}).get("temp"),
            "feels_like": data.get("main", {}).get("feels_like"),
            "humidity": data.get("main", {}).get("humidity"),
            "description": data.get("weather", [{}])[0].get("description"),
            "wind_speed": data.get("wind", {}).get("speed"),
            "units": "°C" if units == "metric" else "°F" if units == "imperial" else "K"
        }

    except requests.exceptions.RequestException as e:
        return {"error": f"API request failed: {str(e)}"}

# Triggering the server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)