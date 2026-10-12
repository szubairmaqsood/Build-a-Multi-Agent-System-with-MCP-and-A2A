
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import asyncio
from os import system
from fastmcp import FastMCP, Client
from protocol.post_office import (
    send_message,
    read_messages,
    clear_messages,
)

# Initialize the Scout MCP server
mcp = FastMCP("Scout Agent")

# Connect only to the Contextualist agent for now
CONTEXTUALIST_URL = "http://127.0.0.1:8000/mcp"


async def wait_for_response(task_id: str, timeout: int = 10):
    """Wait for a response from the Contextualist agent."""
    start = asyncio.get_running_loop().time()

    while asyncio.get_running_loop().time() - start < timeout:
        messages = read_messages()

        for msg in messages:
            if (
                msg.get("task_id") == task_id
                and msg.get("recipient") == "scout"
            ):
                return msg

        await asyncio.sleep(0.5)

    return None


@mcp.tool
async def scout(topic: str, city: str, task_id: str = "task-1"):
    """Collect contextual information for a topic and city."""

    # Clear old messages before starting
    clear_messages()

    # Connect only to Contextualist
    async with Client(CONTEXTUALIST_URL) as contextualist_client:

        # Request contextual information
        await contextualist_client.call_tool(
            "contextualize",
            {
                "topic": topic,
                "city": city,
                "task_id": task_id,
            },
        )

        # Wait for Contextualist to publish its response
        response = await wait_for_response(task_id)

        if response is None:
            return {
                "error": "Contextualist did not respond before timeout",
                "task_id": task_id,
            }

        context = response["payload"]

    # Build the result without media
    final_signal = {
        "topic": topic,
        "location": city,
        "context": context,
        "media": [],
    }

    # Publish the result for the Publisher agent
    send_message({
        "sender": "scout",
        "recipient": "publisher",
        "task_id": task_id,
        "status": "done",
        "payload": final_signal,
    })

    print(final_signal)
    return final_signal


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8004,
    )
