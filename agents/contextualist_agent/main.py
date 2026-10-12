import os
import asyncio
import json
from fastmcp import FastMCP, Client
from contextlib import AsyncExitStack

# Import the lightweight messaging layer used across agents
from synapse.protocol.post_office import send_message, read_messages

# Create the FastMCP server for this agent
mcp = FastMCP("Contextualist Agent")

# Upstream MCP services this agent depends on
WORLD_DATA_URL = "http://0.0.0.0:8001/mcp"
FINANCE_URL = "http://0.0.0.0:8002/mcp"


@mcp.tool
async def contextualize(topic: str, city: str, task_id: str = "task-1"):
    """
    Fetches contextual data for a topic and city.
    This agent combines:
    - News headline(s)
    - Current weather
    - FX conversion rate
    Then it publishes a structured "signal" for downstream agents.
    """

    # AsyncExitStack helps you manage multiple async clients safely
    # so they always close properly when the function finishes.
    async with AsyncExitStack() as stack:
        # Create MCP clients for upstream tool servers
        world_client = await stack.enter_async_context(Client(WORLD_DATA_URL))
        finance_client = await stack.enter_async_context(Client(FINANCE_URL))

        # Run all tool calls concurrently for better performance
        results = await asyncio.gather(
            world_client.call_tool("search_news", {"query": topic}),
            world_client.call_tool("get_weather", {"city": city}),
            finance_client.call_tool("get_fx_rate", {"location": city})
        )

        # Extract the tool response payloads
        news, weather, fx = [r.data for r in results]

    # Build a single structured object that downstream agents can rely on
    signal = {
        "topic": topic,
        "news_headline": news.get("headline"),
        "location": {
            "city": city,
            "weather": f"{weather.get('temperature')}°C, {weather.get('description')}"
        },
        "financial_context": fx,
    }

    # Send message to the post office so the Scout agent can pick it up later
    send_message({
        "sender": "contextualist",
        "recipient": "scout",
        "task_id": task_id,
        "status": "done",
        "payload": signal
    })

    # Return the signal for direct tool consumers as well
    return signal


if __name__ == "__main__":
    # Start the MCP server for this agent
    # This will expose the tool at: http://0.0.0.0:8000/mcp
    mcp.run(transport="http", host="0.0.0.0", port=8000)