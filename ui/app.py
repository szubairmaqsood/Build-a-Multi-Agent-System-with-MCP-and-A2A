
# ============================================
# SYNAPSE - Context Aware Reports
# Streamlit User Interface
# ============================================

# Imports
import os
import json
import asyncio

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from fastmcp import Client


# ============================================
# Environment Configuration
# ============================================

# Load environment variables from the .env file
load_dotenv()

# MCP agent URLs
SCOUT_URL = "http://127.0.0.1:8004/mcp"
PUBLISHER_URL = "http://127.0.0.1:8005/mcp"

# Fetch the OpenRouter API key
api_key = os.getenv("OPENROUTER_API_KEY")

# OpenRouter client
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)


# ============================================
# MCP Helper
# ============================================

# Connect to an MCP server and call the requested tool
async def call_tool(url: str, tool: str, params: dict):
    async with Client(url) as mcp_client:
        result = await mcp_client.call_tool(tool, params)
        return result.data


# ============================================
# Location Detection
# ============================================

# Identify the primary country and its capital
def get_location_context(news_text: str) -> dict:
    prompt = f"""
    Identify the primary country related to this news topic.

    Return only a valid JSON object with these keys:
    {{
        "country": "country name",
        "capital": "capital city"
    }}

    If no country can be identified, use:
    {{
        "country": "United States",
        "capital": "Washington, D.C."
    }}

    News topic: {news_text}
    """

    response = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": (
                    "Return only a valid JSON object. "
                    "Do not include Markdown or explanations."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=200
    )

    # Extract the model response
    content = response.choices[0].message.content

    # Check for an empty response
    if not content or not content.strip():
        raise ValueError(
            "OpenRouter returned an empty response. Please try again."
        )

    # Print the response in the terminal for debugging
    print("Location AI response:", repr(content))

    # Parse and validate the JSON response
    try:
        data = json.loads(content)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"OpenRouter returned invalid JSON: {content!r}"
        ) from error

    # Ensure the required fields exist
    if not data.get("country") or not data.get("capital"):
        raise ValueError(
            f"The AI response is missing country or capital: {data}"
        )

    return data


# ============================================
# Scout Agent
# ============================================

# Send the topic and detected city to Scout
def run_scout(topic: str, city: str):
    return asyncio.run(
        call_tool(
            SCOUT_URL,
            "scout",
            {
                "topic": topic,
                "city": city
            }
        )
    )


# ============================================
# Publisher Agent
# ============================================

# Send Scout's research payload to Publisher
def run_publisher(payload: dict):
    return asyncio.run(
        call_tool(
            PUBLISHER_URL,
            "publish_brief",
            {
                "payload": payload
            }
        )
    )


# ============================================
# Streamlit Interface
# ============================================

st.title("SYNAPSE - Context Aware Reports")

st.write(
    "Generate context-aware reports using your MCP agents."
)

# Topic input
topic = st.text_input(
    "Topic",
    "Semiconductor factory opening in Japan"
)


# ============================================
# Report Generation
# ============================================

# Run the workflow only when the user clicks the button
if st.button("Generate Report"):

    if not api_key:
        st.error(
            "OPENROUTER_API_KEY is missing. "
            "Please check your .env file."
        )

    elif not topic.strip():
        st.warning("Please enter a topic.")

    else:
        try:
            # Step 1: Detect the country and capital
            with st.spinner("Identifying location..."):
                location_data = get_location_context(topic)
                city = location_data["capital"]

            st.write(
                f"**Detected country:** {location_data['country']}"
            )
            st.write(f"**Using city:** {city}")

            # Step 2: Run the Scout agent
            with st.spinner("Running Scout..."):
                scout_data = run_scout(topic, city)

            # Step 3: Normalize image data if available
            # Media is optional, so continue if no images exist.
            try:
                images = scout_data.get("media", {}).get(
                    "images", []
                )

                for img in images:
                    if isinstance(img.get("src"), str):
                        img["src"] = {
                            "url": img["src"],
                            "type": "image"
                        }

            except (AttributeError, TypeError):
                pass

            # Step 4: Run the Publisher agent
            with st.spinner("Running Publisher..."):
                publisher_data = run_publisher(scout_data)

            # Step 5: Display the final article
            st.subheader("Final Article")

            article = publisher_data.get(
                "article",
                "No article was returned."
            )

            st.markdown(
                article,
                unsafe_allow_html=True
            )

            # Step 6: Display the returned payload
            st.subheader("Payload")

            st.json(
                publisher_data.get("payload", scout_data)
            )

        except Exception as error:
            st.error(
                f"Report generation failed: {error}"
            )

            # Full details are printed in the terminal
            print("Report generation error:", repr(error))
