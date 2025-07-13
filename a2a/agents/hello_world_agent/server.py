import click
import logging
import sys
import uvicorn
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from server_agent_executor import (
    HelloWorldAgentExecutor,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option('--host', 'host', default='localhost')
@click.option('--port', 'port', default=9999)
def main(host, port):
    """Starts the HelloWorld Agent server."""
    try:
        # Define the skills for the agent
        skill = AgentSkill(
            id='hello_world',
            name='Returns hello world',
            description='Just returns hello world',
            tags=['hello world'],
            examples=['hi', 'hello world'],
        )

        # Define an extended skill for authenticated users
        extended_skill = AgentSkill(
            id='super_hello_world',
            name='Returns a SUPER Hello World',
            description='A more enthusiastic greeting, only for authenticated users.',
            tags=['hello world', 'super', 'extended'],
            examples=['super hi', 'give me a super hello'],
        )

        # Initialize the public agent card
        public_agent_card = AgentCard(
            name='Hello World Agent',
            description='Just a hello world agent',
            url='http://localhost:9999/',
            version='1.0.0',
            defaultInputModes=['text'],
            defaultOutputModes=['text'],
            capabilities=AgentCapabilities(streaming=True),
            skills=[skill],  # Only the basic skill for the public card
            supportsAuthenticatedExtendedCard=True,
        )

        # This will be the authenticated extended agent card
        # It includes the additional 'extended_skill'
        specific_extended_agent_card = public_agent_card.model_copy(
            update={
                'name': 'Hello World Agent - Extended Edition',  # Different name for clarity
                'description': 'The full-featured hello world agent for authenticated users.',
                'version': '1.0.1',  # Could even be a different version
                # Capabilities and other fields like url, defaultInputModes, defaultOutputModes,
                # supportsAuthenticatedExtendedCard are inherited from public_agent_card unless specified here.
                'skills': [
                    skill,
                    extended_skill,
                ],  # Both skills for the extended card
            }
        )

        # Initialize the request handler
        request_handler = DefaultRequestHandler(
            agent_executor=HelloWorldAgentExecutor(),
            task_store=InMemoryTaskStore(),
        )

        # Create the server instance
        server = A2AStarletteApplication(
            agent_card=public_agent_card,
            http_handler=request_handler,
            extended_agent_card=specific_extended_agent_card,
        )

        # Run the server
        uvicorn.run(server.build(), host=host, port=port)
        logger.info(f'Server started at http://{host}:{port}/')
    except Exception as e:
        logger.error(f'An error occurred during server startup: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
