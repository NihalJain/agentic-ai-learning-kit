import click
import httpx
import logging
import os
import sys
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryPushNotifier, InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from dotenv import load_dotenv

from server_agent import CurrencyAgent
from server_agent_executor import CurrencyAgentExecutor

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MissingAPIKeyError(Exception):
    """Exception for missing API key."""


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=10000)
def main(host, port):
    """Starts the Currency Agent server."""
    try:
        if not os.getenv('LLM_MODEL_PROVIDER'):
            raise MissingAPIKeyError('LLM_MODEL_PROVIDER environment variable not set.')
        if not os.getenv('LLM_API_KEY'):
            raise MissingAPIKeyError('LLM_API_KEY environment variable not set.')
        if os.getenv('MOCK_CURRENCY_ENDPOINT', 'false').lower() == 'true':
            logger.info('Mock currency endpoint is enabled')
        else:
            logger.info('Mock currency endpoint is disabled')

        # Initialize capabilities for the agent
        capabilities = AgentCapabilities(streaming=True, pushNotifications=True)

        # Define the skills for the agent
        skill = AgentSkill(
            id='convert_currency',
            name='Currency Exchange Rates Tool',
            description='Helps with exchange values between various currencies',
            tags=['currency conversion', 'currency exchange'],
            examples=['What is exchange rate between USD and GBP?'],
        )

        # Initialize the public agent card
        agent_card = AgentCard(
            name='Currency Agent',
            description='Helps with exchange rates for currencies',
            url=f'http://{host}:{port}/',
            version='1.0.0',
            defaultInputModes=CurrencyAgent.SUPPORTED_CONTENT_TYPES,
            defaultOutputModes=CurrencyAgent.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=[skill],
        )

        # Initialize the request handler
        httpx_client = httpx.AsyncClient()
        request_handler = DefaultRequestHandler(
            agent_executor=CurrencyAgentExecutor(),
            task_store=InMemoryTaskStore(),
            push_notifier=InMemoryPushNotifier(httpx_client),
        )

        # Create the server instance
        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler
        )

        # Run the server
        uvicorn.run(server.build(), host=host, port=port)
        logger.info(f'Server started at http://{host}:{port}/')
    except MissingAPIKeyError as e:
        logger.error(f'Error: {e}')
        sys.exit(1)
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
