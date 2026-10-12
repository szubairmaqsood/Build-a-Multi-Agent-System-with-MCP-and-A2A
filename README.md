# Synapse — Context-Aware AI Reporting System

Synapse is an AI-powered reporting system that generates context-aware daily briefs for a given topic and city. It gathers information from multiple external sources, coordinates data collection through AI agents, and transforms the collected information into a structured, readable report.

The system uses **Model Context Protocol (MCP)** to expose external APIs as tools, **OpenRouter** to access LLMs, and **Streamlit** to provide an interactive user interface.

## Key Features

- **Context-aware reporting:** Generate reports based on a user-provided topic and city.
- **Multi-source data collection:** Gather relevant news, weather, financial information, and images.
- **Agent-based workflow:** Separate information gathering from article generation.
- **MCP integration:** Expose external APIs through reusable MCP tools.
- **LLM-powered publishing:** Generate structured articles using models available through OpenRouter.
- **Source transparency:** Present supporting sources and context alongside generated reports.
- **Interactive interface:** Enter a topic and location and view the resulting report in Streamlit.

## Architecture

Synapse consists of three main layers.

### 1. MCP Servers

Independent servers expose external data sources as tools.

- **World Data:** News, weather, and other contextual information.
- **Finance:** Financial data and market information.
- **Media Engine:** Relevant images and media resources.

### 2. Agents

Agents coordinate the workflow.

- **Scout Agent:** Collects and organizes relevant information from MCP servers.
- **Publisher Agent:** Uses the collected information and an LLM through OpenRouter to generate the final report.

### 3. User Interface

The Streamlit application allows users to enter a topic and city, trigger report generation, and view the resulting article with its supporting context.

## Project Structure

```text
synapse/
├── agents/
│   ├── scout_agent/
│   └── publisher_agent/
├── mcp-servers/
│   ├── world-data/
│   ├── finance/
│   └── media-engine/
├── protocol/
│   └── post_office.py
├── ui/
│   └── app.py
├── synapse_env/
├── .env
├── .env.example
├── .gitignore
└── README.md
```

> `synapse_env/` is the local Python virtual environment. It should remain excluded from version control.

## How It Works

1. The user enters a topic and city in the Streamlit interface.
2. The Scout Agent identifies and collects relevant information using MCP tools.
3. The collected information is organized into signals containing useful context and source details.
4. The Publisher Agent prepares the collected information for report generation.
5. An LLM accessed through OpenRouter generates a structured daily brief.
6. Streamlit displays the article and its supporting information.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application and agent development |
| Model Context Protocol (MCP) | Standardized access to external tools |
| OpenRouter | LLM API gateway |
| Streamlit | Interactive user interface |
| External APIs | News, weather, finance, and media retrieval |
| Git | Version control |

The specific model and external API providers will be selected during implementation.

## Getting Started

### Prerequisites

- Python 3
- Git
- An OpenRouter API key
- API credentials for external data providers, when required

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd synapse
```

### 2. Create and Activate the Virtual Environment

On Windows CMD:

```bat
py -3 -m venv reporting_env
reporting_env\Scripts\activate
```

Verify the Python installation:

```bat
python --version
```

### 3. Configure Environment Variables

Create a local environment file from the template:

```bat
copy .env.example .env
```

Configure the following variables in `.env`:

```dotenv
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_MODEL=your_preferred_model
OPENROUTER_SITE_URL=http://localhost:8501
OPENROUTER_APP_NAME=Synapse
```

Replace the placeholder values with your actual configuration. Never commit `.env` or expose API keys in source code.

### 4. Install Dependencies

Dependencies will be added as the individual components are implemented. Refer to the project instructions as development progresses.

### 5. Run the Application

The application is not runnable yet. The MCP servers, agents, and Streamlit interface will be implemented incrementally.

## Development Roadmap

- [ ] Establish the project structure and configuration.
- [ ] Implement the World Data MCP server.
- [ ] Implement the Finance MCP server.
- [ ] Implement the Media Engine MCP server.
- [ ] Define the shared communication protocol in `protocol/post_office.py`.
- [ ] Implement the Scout Agent.
- [ ] Implement the Publisher Agent using OpenRouter.
- [ ] Build the Streamlit interface.
- [ ] Integrate the complete reporting workflow.
- [ ] Add testing, logging, error handling, and source validation.

## Design Principles

- Keep MCP servers independent and reusable.
- Separate data collection from report generation.
- Use environment variables for secrets and configuration.
- Preserve source URLs and timestamps for traceability.
- Distinguish verified information from AI-generated interpretation.
- Handle unavailable data sources gracefully.
- Avoid presenting generated content as verified fact without supporting evidence.
