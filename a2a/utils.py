from a2a.client import A2ACardResolver
from a2a.types import AgentCard, SendMessageRequest, SendStreamingMessageRequest, JSONRPCResponse
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty
from rich.table import Table

from constants import EXTENDED_AGENT_CARD_PATH


def print_agent_card(card: AgentCard, console: Console):
    """Prints the agent card in a structured format."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column()

    table.add_row("Name", card.name)
    table.add_row("Description", card.description)
    table.add_row("URL", card.url)
    table.add_row("Version", card.version)
    if card.capabilities:
        table.add_row("Streaming", str(card.capabilities.streaming))
        if card.capabilities.pushNotifications is not None:
            table.add_row("Push Notifications", str(card.capabilities.pushNotifications))
    table.add_row("Supports Auth", str(card.supportsAuthenticatedExtendedCard))

    if card.skills:
        skills_table = Table(box=None, show_header=True, header_style="bold magenta")
        skills_table.add_column("ID")
        skills_table.add_column("Name")
        skills_table.add_column("Description")
        for skill in card.skills:
            skills_table.add_row(skill.id, skill.name, skill.description)
        table.add_row("Skills", skills_table)

    console.print(Panel(table, title="[bold]Agent Card[/bold]", border_style="blue", expand=False))


def print_request(request: SendMessageRequest | SendStreamingMessageRequest, console: Console):
    """Prints the request in a structured format."""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="cyan", no_wrap=True)
    table.add_column()

    table.add_row("Request ID", request.id)
    if request.params.message.role:
        table.add_row("Role", request.params.message.role)
    if request.params.message.messageId:
        table.add_row("Message ID", request.params.message.messageId)
    if request.params.message.taskId:
        table.add_row("Task ID", request.params.message.taskId)
    if request.params.message.contextId:
        table.add_row("Context ID", request.params.message.contextId)

    if request.params.message.parts:
        for part in request.params.message.parts:
            if hasattr(part.root, 'text'):
                table.add_row("Content", part.root.text)

    title = "Sent "
    if isinstance(request, SendStreamingMessageRequest):
        title += "Streaming "
    title += "Message"
    console.print(Panel(table, title=f"[bold]{title}[/bold]", border_style="yellow", expand=False))


def print_response(response: JSONRPCResponse | dict, console: Console, title: str = "Received Response"):
    """Prints the response in a structured format."""
    if isinstance(response, dict):
        pretty_response = Pretty(response)
    else:
        pretty_response = Pretty(response.model_dump(mode='json', exclude_none=True))
    console.print(Panel(pretty_response, title=f"[bold]{title}[/bold]", border_style="green", expand=False))


async def get_agent_card(resolver: A2ACardResolver, console: Console) -> AgentCard:
    """Fetches the agent card, preferring the authenticated extended card if available."""
    console.print(
        f"[yellow]Attempting to fetch public agent card from: {resolver.base_url}/{resolver.agent_card_path}[/yellow]")
    public_card = await resolver.get_agent_card()
    console.print("[green]Successfully fetched public agent card.[/green]")
    print_agent_card(public_card, console)

    if public_card.supportsAuthenticatedExtendedCard:
        try:
            console.print("[yellow]Attempting to fetch authenticated extended card...[/yellow]")
            extended_card = await resolver.get_agent_card(
                relative_card_path=EXTENDED_AGENT_CARD_PATH,
                http_kwargs={'headers': {'Authorization': 'Bearer dummy-token-for-extended-card'}},
            )
            console.print("[green]Successfully fetched authenticated extended agent card.[/green]")
            print_agent_card(extended_card, console)
            return extended_card
        except Exception as e:
            console.print(f"[red]Failed to fetch extended agent card: {e}. Proceeding with public card.[/red]")
    return public_card
