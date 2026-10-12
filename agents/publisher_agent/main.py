
import os
import json
from openai import OpenAI
from fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Initialize the Publisher MCP server
mcp = FastMCP("Publisher Agent")


@mcp.tool
async def publish_brief(payload: dict) -> dict:
    """Generate a daily brief using an OpenRouter free model."""

    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        return {
            "error": "OPENROUTER_API_KEY is missing from .env"
        }

    # Prepare the prompt
    prompt = f"""
You are a professional news writer.

Using the supplied data, write a short daily brief.

Rules:
- Use a neutral journalistic tone.
- Do not invent facts.
- If data is missing, write "Not available."
- Include a headline.
- Include 2-3 paragraphs.
- Include a short "Why it matters" section.
- Include an "About the place of news" section.
- Mention the weather and conversion rate only if provided.
- If either is missing, state "Not available."

Data:
{json.dumps(payload, indent=2, ensure_ascii=False)}
"""

    # Connect to OpenRouter using the OpenAI SDK
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    # Generate the brief
    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        max_tokens=1500,
    )

    article = response.choices[0].message.content

    if not article:
        return {
            "error": "The model returned an empty response",
            "payload": payload,
        }

    return {
        "article": article.strip(),
        "payload": payload,
    }


if __name__ == "__main__":
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8005,
    )
