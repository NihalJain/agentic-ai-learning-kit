import httpx
import os
from collections.abc import AsyncIterable
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel
from typing import Any, Literal
from unittest.mock import file_spec

memory = MemorySaver()


@tool
def get_exchange_rate(
        currency_from: str = 'USD',
        currency_to: str = 'EUR',
        currency_date: str = 'latest',
):
    """Use this to get current exchange rate.

    Args:
        currency_from: The currency to convert from (e.g., "USD").
        currency_to: The currency to convert to (e.g., "EUR").
        currency_date: The date for the exchange rate or "latest". Defaults to
            "latest".

    Returns:
        A dictionary containing the exchange rate data, or an error message if
        the request fails.
    """
    try:
        if os.getenv('MOCK_CURRENCY_ENDPOINT', 'false').lower() == 'true':
            # Below is a mock implementation for testing purposes.
            import json
            file_path = os.path.join(os.path.dirname(__file__), 'mock_data', 'currency_data.json')
            response = json.load(open(file_path))
            if 'rates' not in response:
                return {'error': 'Invalid API response format.'}
            print(
                f'Exchange rate from {currency_from} to {currency_to} on {currency_date}: {response["rates"].get(currency_to, "N/A")}')
            return response

        # If mocking is disabled, we do a real call as below
        response = httpx.get(
            f'https://api.frankfurter.app/{currency_date}',
            params={'from': currency_from, 'to': currency_to},
        )
        response.raise_for_status()

        data = response.json()
        if 'rates' not in data:
            return {'error': 'Invalid API response format.'}
        return data
    except httpx.HTTPError as e:
        print(f'HTTP error occurred: {e}')
        return {'error': f'API request failed: {e}'}
    except ValueError as e:
        print(f'Invalid JSON response from API. {e}')
        return {'error': 'Invalid JSON response from API.'}


class ResponseFormat(BaseModel):
    """Respond to the user in this format."""

    status: Literal['input_required', 'completed', 'error'] = 'input_required'
    message: str


class CurrencyAgent:
    """CurrencyAgent - a specialized assistant for currency convesions."""

    SYSTEM_INSTRUCTION = (
        'You are a specialized assistant for currency conversions. '
        "Your sole purpose is to use the 'get_exchange_rate' tool to answer questions about currency exchange rates. "
        'If the user asks about anything other than currency conversion or exchange rates, '
        'politely state that you cannot help with that topic and can only assist with currency-related queries. '
        'Do not attempt to answer unrelated questions or use tools for other purposes.'
    )

    FORMAT_INSTRUCTION = (
        'Set response status to input_required if the user needs to provide more information to complete the request.'
        'Set response status to error if there is an error while processing the request.'
        'Set response status to completed if the request is complete.'
    )

    def __init__(self):
        model_source = os.getenv('LLM_MODEL_PROVIDER', 'google').lower()

        if model_source == 'google':
            self.model = ChatGoogleGenerativeAI(
                model=os.getenv('LLM_MODEL_NAME', 'gemini-2.5-pro'),
                google_api_key=os.getenv('LLM_API_KEY'),
                temperature=os.getenv('LLM_TEMPERATURE', 0),
            )
        elif model_source == 'openai':
            self.model = ChatOpenAI(
                openai_api_base=os.getenv('LLM_BASE_URL', 'https://api.openai.com/v1/'),
                model=os.getenv('LLM_MODEL_NAME', 'gpt-4o-mini'),
                openai_api_key=os.getenv('LLM_API_KEY'),
                temperature=os.getenv('LLM_TEMPERATURE', 0),
            )
        else:
            raise ValueError(
                "Unsupported model source: "
                f"'{model_source}'. Please set LLM_MODEL_PROVIDER to 'google' or 'openai'."
            )

        self.tools = [get_exchange_rate]

        self.graph = create_react_agent(
            self.model,
            tools=self.tools,
            checkpointer=memory,
            prompt=self.SYSTEM_INSTRUCTION,
            response_format=(self.FORMAT_INSTRUCTION, ResponseFormat),
            debug=False
        )

    async def stream(self, query, context_id) -> AsyncIterable[dict[str, Any]]:
        inputs = {'messages': [('user', query)]}
        config = {'configurable': {'thread_id': context_id}}

        print(f'Starting agent with inputs: {inputs} and config: {config}')
        for item in self.graph.stream(inputs, config, stream_mode='values'):
            message = item['messages'][-1]
            if (
                    isinstance(message, AIMessage)
                    and message.tool_calls
                    and len(message.tool_calls) > 0
            ):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Looking up the exchange rates...',
                }
            elif isinstance(message, ToolMessage):
                yield {
                    'is_task_complete': False,
                    'require_user_input': False,
                    'content': 'Processing the exchange rates..',
                }

        agent_response = self.get_agent_response(config)
        print(f'Agent response: {agent_response}')
        yield agent_response

    def get_agent_response(self, config):
        current_state = self.graph.get_state(config)
        structured_response = current_state.values.get('structured_response')
        if structured_response and isinstance(
                structured_response, ResponseFormat
        ):
            if structured_response.status == 'input_required':
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'error':
                return {
                    'is_task_complete': False,
                    'require_user_input': True,
                    'content': structured_response.message,
                }
            if structured_response.status == 'completed':
                return {
                    'is_task_complete': True,
                    'require_user_input': False,
                    'content': structured_response.message,
                }

        return {
            'is_task_complete': False,
            'require_user_input': True,
            'content': (
                'We are unable to process your request at the moment. '
                'Please try again.'
            ),
        }

    SUPPORTED_CONTENT_TYPES = ['text', 'text/plain']
