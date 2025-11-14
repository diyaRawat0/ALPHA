from rich.console import Console
from rich.live import Live
import time

console = Console()

print("--- DEBUG: Simple Live Script Started ---") # This should always print

try:
    # This creates a Live display that updates a simple message
    with Live("[bold green]Hello from Rich Live![/bold green]", screen=True, refresh_per_second=1) as live:
        console.print("--- DEBUG: Entered simple Live context ---") # This print might disappear quickly if screen=True is active

        # The loop updates the content displayed by Live
        for i in range(10):
            live.update(f"[bold blue]Updating... {i+1}/10[/bold blue]")
            time.sleep(1) # Wait 1 second between updates

        # Display a final message and keep it visible briefly
        live.update("[bold yellow]Simple Live Test Complete![/bold yellow]")
        time.sleep(2) # Keep the final message on screen for 2 seconds

except KeyboardInterrupt:
    console.print("\n[bold red]DEBUG: Interrupted by user (Ctrl+C).[/bold red]")
except Exception as e:
    console.print(f"\n[bold red]DEBUG: An unexpected error occurred: {e}[/bold red]")
    console.print_exception(show_locals=True) # Shows a detailed traceback

console.print("--- DEBUG: Simple Live Script Finished ---") # This should print after Live exits