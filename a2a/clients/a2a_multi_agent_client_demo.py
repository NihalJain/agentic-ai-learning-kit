import os
import sys

# Add the parent directory to the Python path to allow imports from a2a
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from uuid import uuid4

import httpx
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendStreamingMessageRequest,
)
from rich.console import Console

from constants import PUBLIC_AGENT_CARD_PATH, EXTENDED_AGENT_CARD_PATH
from utils import get_agent_card, print_request, print_response


async def main() -> None:
    """Demonstrates a multi-agent scenario where a client interacts with two different agents."""
    console = Console()
    console.print("[bold cyan]Starting Multi-Agent Demo...[/bold cyan]")

    async with httpx.AsyncClient() as httpx_client:
        # --- Interaction 1: HelloWorldAgent ---
        hello_agent_port = 9999
        hello_agent_url = f"http://localhost:{hello_agent_port}"
        console.print(f"\n[bold cyan]Step 1: Interacting with HelloWorldAgent on port {hello_agent_port}[/bold cyan]")

        try:
            # Initialize resolver and client for HelloWorldAgent
            hello_resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=hello_agent_url,
                agent_card_path=PUBLIC_AGENT_CARD_PATH,
            )
            hello_agent_card = await get_agent_card(hello_resolver, console)
            hello_client = A2AClient(httpx_client=httpx_client, agent_card=hello_agent_card)

            # Send a message to HelloWorldAgent
            hello_message_payload = {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": "Hello"}],
                    "messageId": uuid4().hex,
                },
            }
            hello_request = SendMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(**hello_message_payload),
            )

            print_request(hello_request, console)
            hello_response = await hello_client.send_message(hello_request)
            print_response(hello_response, console, title="Response from HelloWorldAgent")

        except httpx.ConnectError:
            console.print(
                f"[bold red]Error:[/bold red] Could not connect to the HelloWorldAgent on port {hello_agent_port}.")
            console.print(
                "[yellow]Please ensure the HelloWorldAgent server is running:[/yellow] `python a2a/agents/hello_world_agent/server.py`")
            return

        # --- Interaction 2: CurrencyAgent ---
        currency_agent_port = 10000
        currency_agent_url = f"http://localhost:{currency_agent_port}"
        console.print(f"\n[bold cyan]Step 2: Interacting with CurrencyAgent on port {currency_agent_port}[/bold cyan]")

        try:
            # Initialize resolver and client for CurrencyAgent
            currency_resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=currency_agent_url,
                agent_card_path=PUBLIC_AGENT_CARD_PATH,
            )
            currency_agent_card = await get_agent_card(currency_resolver, console)
            currency_client = A2AClient(httpx_client=httpx_client, agent_card=currency_agent_card)

            # Send a streaming message to CurrencyAgent
            currency_message_payload = {
                "message": {
                    "role": "user",
                    "parts": [{"kind": "text", "text": "how much is 25 USD in INR?"}],
                    "messageId": uuid4().hex,
                },
            }
            currency_request = SendStreamingMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(**currency_message_payload),
            )

            print_request(currency_request, console)
            stream_response = currency_client.send_message_streaming(currency_request)

            async for chunk in stream_response:
                print_response(chunk.model_dump(mode='json', exclude_none=True), console,
                               title="Streaming Response from CurrencyAgent")

        except Exception:
            console.print(
                f"[bold red]Error:[/bold red] Could not connect to the CurrencyAgent on port {currency_agent_port}.")
            console.print(
                "[yellow]Please ensure the CurrencyAgent server is running:[/yellow] `python a2a/agents/currency_agent/server.py`")
            return

    console.print("\n[bold cyan]Multi-Agent Demo finished.[/bold cyan]")


if __name__ == "__main__":
    asyncio.run(main())
