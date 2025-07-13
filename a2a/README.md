# A2A Client Demo

This project provides a hands-on demonstration of the Agent-to-Agent (A2A) protocol, showcasing how an agent (acting as
a client) can interact with multiple, specialized remote agents. It includes two distinct remote agents, a
`HelloWorldAgent` and a `CurrencyAgent`, and two client demos that highlight different interaction scenarios.

## Key Concepts Demonstrated

This project is designed to illustrate several core concepts in agent-based systems:

- **Agent-to-Agent (A2A) Communication:** The fundamental pattern of direct communication between autonomous agents.
- **Client as an Agent:** The client application itself is an agent, capable of initiating communication and
  orchestrating workflows with other remote agents.
- **Service Discovery:** How a client agent can discover the capabilities of a remote agent by fetching its "agent
  card."
- **Authenticated vs. Public Capabilities:** The concept of a remote agent exposing different sets of skills or
  information based on whether the client is authenticated.
- **Streaming and Non-Streaming Responses:** The client demos show how to handle both simple, single-shot responses and
  continuous streams of data from a remote agent.
- **Task Lifecycle Management:** The `CurrencyAgent` demo illustrates how to manage a multi-step task, including status
  updates and handling of artifacts.
- **Multi-Agent Workflows:** The multi-agent demo showcases how a client agent can orchestrate a workflow that involves
  multiple, specialized remote agents to accomplish a goal.

## The Agents

This project includes two remote agents, each designed to demonstrate different capabilities.

### `HelloWorldAgent`

A simple agent that demonstrates the basics of A2A communication. It exposes two skills:

- **`hello_world`:** A public skill that returns a simple greeting.
- **`super_hello_world`:** An authenticated skill that returns a more enthusiastic greeting.

This agent is ideal for understanding the core concepts of agent cards and authenticated skills.

### `CurrencyAgent`

A more advanced agent that demonstrates a practical use case for agent-based systems. It can convert currencies and
provides the following features:

- **Tool-Using Agent:** It uses a `get_exchange_rate` tool to fetch currency exchange rates.
- **Streaming Responses:** It streams its progress back to the client, providing real-time updates.
- **Multi-Turn Conversations:** It can engage in a multi-turn conversation to clarify information or answer follow-up
  questions.
- **Mockable Endpoints:** It can be configured to use a mock endpoint for currency data, allowing for offline
  development and testing.

## The Client Demos

This project includes two client demos, each designed to showcase a different interaction pattern for the client agent.

### Single-Agent Client Demo (`a2a/clients/a2a_single_agent_client_demo.py`)

This demo shows the client agent interacting with a single *remote* agent (`HelloWorldAgent` or `CurrencyAgent`) at a
time. It is ideal for exploring the capabilities of each remote agent in isolation.

### Multi-Agent Client Demo (`a2a/clients/a2a_multi_agent_client_demo.py`)

This demo showcases a simple multi-agent workflow where the client agent orchestrates interactions with multiple
*remote* agents. The client agent first connects to the `HelloWorldAgent` to get a greeting, and then it connects to the
`CurrencyAgent` to perform a currency conversion. This demonstrates how a client agent can leverage the specialized
capabilities of different remote agents to achieve a combined outcome.

## Project Structure

- **`agents/`**: Contains the implementations of various agents.
    - **`agents/currency_agent/`**: Contains the `CurrencyAgent` server and its related files.
    - **`agents/hello_world_agent/`**: Contains the `HelloWorldAgent` server and its related files.
- **`clients/`**: Contains the client demo applications.
    - **`clients/a2a_single_agent_client_demo.py`**: The entry point for the single-agent client demo.
    - **`clients/a2a_multi_agent_client_demo.py`**: The entry point for the multi-agent client demo.
- **`utils.py`**: Contains shared utility functions for the client demos, including structured printing of agent cards,
  requests, and responses.
- **`constants.py`**: Contains constants used by the client and servers.
- **`requirements.txt`**: A list of the Python dependencies for the project.

## Prerequisites

- Python 3.12.7 or higher
- Required Python dependencies listed in `requirements.txt`.

## Setup Instructions

1. **Download the Repository**
   Download this repository to your local machine.

2. **Navigate to the `a2a` directory:**
   ```bash
   cd a2a
   ```

3. **Set Up Virtual Environment**
   Create and activate a Python virtual environment:
   ```bash
   python3 -m venv .venv
   .venv\Scripts\Activate.ps1 # For Windows
   source .venv/bin/activate
   ```

4. **Install Dependencies**
   Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Demos

### Running the Single-Agent Demos

#### Running the HelloWorldAgent

1. **Start the `HelloWorldAgent` server:**
   ```bash
   python agents/hello_world_agent/server.py
   ```

2. **Run the A2A Client Demo to connect to the `HelloWorldAgent`:**
   ```bash
   python clients/a2a_single_agent_client_demo.py 9999
   ```

#### Running the CurrencyAgent

1. **Start the `CurrencyAgent` server:**
   ```bash
   python agents/currency_agent/server.py
   ```

2. **Run the A2A Client Demo to connect to the `CurrencyAgent`:**
   ```bash
   python clients/a2a_single_agent_client_demo.py 10000
   ```

### Running the Multi-Agent Demo

1. **Start the `HelloWorldAgent` server in a separate terminal:**
   ```bash
   python agents/hello_world_agent/server.py
   ```

2. **Start the `CurrencyAgent` server in another terminal:**
   ```bash
   python agents/currency_agent/server.py
   ```

3. **Run the Multi-Agent Client Demo:**
   ```bash
   python clients/a2a_multi_agent_client_demo.py
   ```

## Environment Variables

The `.env` file contains the following environment variables. All `LLM_*` variables are required for the `CurrencyAgent`
to start, as checked by `currency_agent/server.py`.

- `LLM_MODEL_PROVIDER`: **(Required)** Specifies the model provider (`google` or `openai`). Defaults to `google`, if not
  explicitly set.
- `LLM_API_KEY`: **(Required)** The API key for authenticating with the LLM provider.
- `LLM_BASE_URL`: **(Optional)** The base URL of the LLM API. Defaults to
  `https://generativelanguage.googleapis.com/v1beta` for `google` source, or `https://api.openai.com/v1/` for `openai`
  source.
- `LLM_MODEL_NAME`: **(Optional)** The name of the LLM model to use. Defaults to `gemini-2.5-pro` for `google` source,
  or `gpt-4o-mini` for `openai` source.
- `LLM_TEMPERATURE`: **(Optional)** The temperature setting for the LLM. Defaults to `0`.
- `MOCK_CURRENCY_ENDPOINT`: **(Optional)** If set to `true`, the currency agent will use a mock endpoint for exchange
  rates. Defaults to `false`.

## Author Information

For any issues or queries, please contact the author:

* Name: [Nihal Jain](https://www.linkedin.com/in/nihaljain)
* Email: [nihaljain.cs@gmail.com](mailto:nihaljain.cs@gmail.com)
