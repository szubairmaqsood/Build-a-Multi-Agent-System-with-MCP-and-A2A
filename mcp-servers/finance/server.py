
import os
import requests
from urllib.parse import quote
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Create the Finance MCP server
mcp = FastMCP("Finance Monitor Server")


def get_currency_code(location: str) -> dict:
    """
    Find a country's currency using its country name or capital city.
    Returns the currency code and symbol, or an error dictionary.
    """

    location = location.strip()

    if not location:
        return {"error": "Location cannot be empty"}

    # Try searching by country name first, then capital city
    encoded_location = quote(location, safe="")

    urls = [
        f"https://restcountries.com/v3.1/name/{encoded_location}",
        f"https://restcountries.com/v3.1/capital/{encoded_location}"
    ]

    try:
        for url in urls:
            response = requests.get(url, timeout=10)

            # Try the next URL if this search fails
            if response.status_code != 200:
                continue

            countries = response.json()

            if not isinstance(countries, list):
                continue

            # Find a country with currency information
            for country in countries:
                if not isinstance(country, dict):
                    continue

                currencies = country.get("currencies", {})

                if not isinstance(currencies, dict) or not currencies:
                    continue

                code = next(iter(currencies))
                currency = currencies[code]

                if not isinstance(currency, dict):
                    currency = {}

                name_data = country.get("name", {})
                if not isinstance(name_data, dict):
                    name_data = {}

                return {
                    "location": name_data.get("common", location),
                    "currency_code": code,
                    "symbol": currency.get("symbol")
                }

        return {
            "error": f"Could not find currency for '{location}'"
        }

    except (requests.exceptions.RequestException, ValueError) as e:
        return {
            "error": f"Currency lookup failed: {str(e)}"
        }


@mcp.tool
def get_fx_rate(location: str) -> dict:
    """
    Get the exchange rate from the location's currency to USD.
    Example: Tokyo -> JPY to USD.
    """

    # Read the exchange-rate API key from .env
    exchange_api_key = os.getenv("EXCHANGERATE_API_KEY")

    if not exchange_api_key:
        return {
            "error": "EXCHANGERATE_API_KEY not set in .env"
        }

    # Determine the currency for the supplied country or city
    currency_info = get_currency_code(location)

    # Validate the currency lookup response
    if not isinstance(currency_info, dict):
        return {
            "error": "Unexpected currency lookup response",
            "details": str(currency_info)
        }

    if "currency_code" not in currency_info:
        return {
            "error": f"Could not determine currency for '{location}'",
            "details": currency_info
        }

    target = currency_info["currency_code"]

    # Request the exchange rate from the currency to USD
    url = (
        f"https://v6.exchangerate-api.com/v6/"
        f"{exchange_api_key}/pair/{target}/USD"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Ensure the API returned a JSON object
        if not isinstance(data, dict):
            return {
                "error": "Unexpected exchange-rate API response",
                "details": str(data)
            }

        # Check the API's own success status
        if data.get("result") != "success":
            return {
                "error": "Exchange-rate API request failed",
                "details": data
            }

        rate = data.get("conversion_rate")

        if rate is None:
            return {
                "error": "Conversion rate missing from API response",
                "details": data
            }

        # Return the structured result for downstream agents
        return {
            "location": currency_info.get("location", location),
            "currency_code": target,
            "rate": rate,
            "target_currency": "USD",
            "source": "ExchangeRate API"
        }

    except (requests.exceptions.RequestException, ValueError) as e:
        return {
            "error": f"Exchange-rate request failed: {str(e)}"
        }


# Start the Finance MCP server on port 8002
if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8002
    )
