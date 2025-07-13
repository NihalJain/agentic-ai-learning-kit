import os
import sys

# Add the parent directory to the Python path to allow imports from a2a
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from typing import Any
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (AgentCard, MessageSendParams, SendMessageRequest, SendStreamingMessageRequest, )
from rich.console import Console

from constants import PUBLIC_AGENT_CARD_PATH
from utils import get_agent_card, print_request, print_response


async def main(port) -> None:
    # Create a Rich console for styled terminal output
    console = Console()
    console.print("[bold cyan]Starting Single-Agent Demo...[/bold cyan]")
    base_url = 'http://localhost:' + str(port)

    async with httpx.AsyncClient() as httpx_client:
        # Initialize A2ACardResolver
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url, agent_card_path=PUBLIC_AGENT_CARD_PATH)

        # Fetch Agent Card and Initialize Client
        try:
            final_agent_card_to_use = await get_agent_card(resolver, console)

            # Initialize A2AClient with the final agent card to use
            client = A2AClient(httpx_client=httpx_client, agent_card=final_agent_card_to_use)
            console.print('[green]A2AClient initialized![/green]')

            console.print('[cyan]Conversation Flow[/cyan]')
            # set timeout to 60 seconds
            client.httpx_client.timeout = httpx.Timeout(60.0, connect=60.0, read=60.0)

            # Build the payload for sending a message
            send_message_payload: dict[str, Any] = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {
                            'kind': 'text',
                            'text': 'how much is 10 USD in INR?'}
                    ],
                    'messageId': uuid4().hex,
                },
            }

            # Send a streaming message request and print each chunk
            streaming_request = SendStreamingMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(**send_message_payload)
            )
            # Send the message request and print the response
            print_request(streaming_request, console)
            stream_response = client.send_message_streaming(streaming_request)

            # Skip multiturn conversation for HelloWorldAgent
            if port == 9999:
                async for chunk in stream_response:
                    print_response(chunk.model_dump(mode='json', exclude_none=True), console,
                                   title="Streaming Response")
                # Code beyond this point is not supported by HelloWorld Agent
                exit(0)

            # Showcase multiturn conversation
            task_id = None
            contextId = None
            async for chunk in stream_response:
                chunk_data = chunk.model_dump(mode='json', exclude_none=True)
                print_response(chunk_data, console, title="Streaming Response")
                task_id = task_id or chunk.root.result.id
                contextId = contextId or chunk.root.result.contextId

            console.print('[cyan]Using previous task_id and contextId to showcase multiturn conversation[/cyan]')
            while True:
                user_input = input(">>> ")
                if user_input.lower() in {'exit', 'quit'}:
                    console.print('[red]Exiting chat.[/red]')
                    break

                # Build the payload for the next message
                multiturn_send_message_payload: dict[str, Any] = {
                    'message': {
                        'role': 'user',
                        'parts': [
                            {
                                'kind': 'text',
                                'text': user_input
                            }
                        ],
                        'messageId': uuid4().hex,
                        'taskId': task_id,
                        'contextId': contextId,
                    },
                }

                multiturn_request = SendMessageRequest(
                    id=str(uuid4()),
                    params=MessageSendParams(**multiturn_send_message_payload),
                )
                print_request(multiturn_request, console)
                multiturn_response = await client.send_message(multiturn_request)
                print_response(multiturn_response, console)

        except Exception:
            console.print(f"[bold red]Error:[/bold red] Could not connect to the agent on port {port}.")
            console.print("[yellow]Please ensure the agent server is running:[/yellow]")
            return

    console.print("\n[bold cyan]Single-Agent Demo finished.[/bold cyan]")


if __name__ == '__main__':
    import asyncio
    # parse port from command line arguments
    import sys

    port = 10000
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port number: {sys.argv[1]}. Using default port 10000.")

    asyncio.run(main(port))
