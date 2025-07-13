# Agentic AI Starter Kit

This repository serves as a kit for learning how to build Agentic AI applications. Currently, it has code to demonstrate
two key communication patterns: Agent-to-Agent (A2A) communication and Model Context Protocol (MCP) communication. We
will add more concepts in the future.

## Project Structure

- **`a2a/`**: Contains a hands-on demonstration of the Agent-to-Agent (A2A) communication pattern. This includes:
    - Detailed `README.md` for setup and running A2A demos.

- **`mcp/`**: Contains a demonstration of the Model Context Protocol (MCP) communication pattern. This includes:
    - **`clients/`**: Client demo application (`mcp_client_demo.py`).
    - **`servers/`**: Example MCP servers (e.g., `math_server.py`).
    - Detailed `README.md` for setup and running MCP demos.

- **`.env`**: Environment variables for configuring LLM access and other settings.

## Prerequisites

- Python 3.12.7 or higher
- Basic familiarity with Python and command-line operations.

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/NihalJain/agentic-ai-learning-kit.git
   cd agentic-ai-learning-kit
   ```

2. **Set Up Virtual Environment**
   ```bash
   python3 -m venv .venv
   # On Windows:
   .venv\Scripts\Activate.ps1
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the root directory of the project (`agentic-ai--learning-kit`) and populate it with the
   necessary LLM API keys and other configurations.

- `LLM_MODEL_PROVIDER`: **(Required)** Specifies the model provider (`google` or `openai`). Defaults to `google`, if not
  explicitly set.
- `LLM_API_KEY`: **(Required)** The API key for authenticating with the LLM provider.
- `LLM_BASE_URL`: **(Optional)** The base URL of the LLM API. Defaults to
  `https://generativelanguage.googleapis.com/v1beta` for `google` source, or `https://api.openai.com/v1/` for `openai`
  source.
- `LLM_MODEL_NAME`: **(Optional)** The name of the LLM model to use. Defaults to `gemini-2.5-pro` for `google` source,
  or `gpt-4o-mini` for `openai` source.
- `LLM_TEMPERATURE`: **(Optional)** The temperature setting for the LLM. Defaults to `0`.

Refer to the `a2a/README.md` and `mcp/README.md` for detailed information on required environment variables for each
respective demo.

## Running the Demos

To run the demos, navigate into the respective subdirectories and follow their `README.md` instructions:

- **A2A Demos:** See `a2a/README.md` for detailed instructions.
- **MCP Demos:** See `mcp/README.md` for detailed instructions.

## Author Information

For any issues or queries, please contact the author:

* Name: [Nihal Jain](https://www.linkedin.com/in/nihaljain)
* Email: [nihaljain.cs@gmail.com](mailto:nihaljain.cs@gmail.com)