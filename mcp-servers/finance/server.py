import os
import requests
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

mcp = FastMCP("Finance Monitor Server")

# Provided helper function to fetch currency code from a location
def get_currency_code(location: str) -> dict:
    """
    Dynamically find the 3-letter currency code for any country using REST Countries API.
    """
    url = f"https://restcountries.com/v3.1/name/{location}"
    
    try:
        response = requests.get(url, timeout=10)
        
        # If the search fails, try searching as a capital city
        if response.status_code != 200:
            url = f"https://restcountries.com/v3.1/capital/{location}"
            response = requests.get(url, timeout=10)

        if response.status_code == 200:
            data = response.json()[0]
            currencies = data.get("currencies", {})
            if currencies:
                code = list(currencies.keys())[0]
                return {
                    "location": data.get("name", {}).get("common"),
                    "currency_code": code,
                    "symbol": currencies[code].get("symbol")
                }
        
        return {"error": f"Could not find currency for '{location}'", "fallback": "USD"}

    except Exception as e:
        return {"error": str(e), "fallback": "USD"}

#Getting exchange rate from currency to USD
@mcp.tool
def get_fx_rate(location: str) -> dict:
    """
    Get FX rate between two currencies.
    """
    exchange_api_key = os.getenv("EXCHANGE_RATE_API_KEY")

    # Get currency code from provided helper function
    currency_info = get_currency_code(location)
    target = currency_info['currency_code']

    url = f"https://v6.exchangerate-api.com/v6/{exchange_api_key}/pair/{target}/USD"
    
    try:
        response = requests.get(url, timeout=10)
        
        # Handle API errors
        if response.status_code != 200:
            return {"error": f"Could not find currency for '{location}'", "fallback": "USD"}

        data = response.json()
        return {
            "currency_code": currency_info['currency_code'],
            "rate": data['conversion_rate'],
            "source": "ExchangeRate API"
        }

    except Exception as e:
        return {"error": str(e), "fallback": "USD"}

# Calling the MCP server on different port
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8002
    )