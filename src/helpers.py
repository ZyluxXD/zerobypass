#!/usr/bin/env python3
import os
import sys
import time
from Xlib.error import DisplayNameError
import klembord
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

from config import console


# ------------------------------------------------
def can_output_graphics():
    # ok um i said this didn't work and that was true because I never implemented it lol
    if not any(var in os.environ for var in ['DISPLAY', 'WAYLAND_DISPLAY']):
        console.print("[red]No graphical display detected. This needs graphical output to work.[/red]")
        sys.exit(0)


def handle_disclaimer():
    filepath = os.path.join(os.path.dirname(__file__), '../DISCLAIMER.md')
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    disclaimer = Markdown(content)
    panel = Panel(disclaimer, title="⚠ Disclaimer ⚠", border_style="red")
    console.print(panel)
    accepted = Confirm.ask("Do you accept this disclaimer?", choices=["y", "n"])

    if accepted:
        console.clear()
    else:
        console.print("[yellow]Not accepted. The application will exit now.[/yellow]")
        sys.exit(0)


# I cooked on this one :)
def get_text():
    with console.status("[bold]Copy[/bold] the text you want to use onto your clipboard [dim](CTRL-V)[/dim]",
                        spinner="bouncingBar"):
        try:
            last_paste = klembord.get_with_rich_text()
            while True:
                current_paste = klembord.get_with_rich_text()
                if current_paste != last_paste:
                    break
                time.sleep(0.1)  # small delay because yes
        except DisplayNameError:
            console.print("[yellow]Clipboard access failed. Falling back to manual input.[/yellow]")
            current_paste = console.input("Paste text here and press Enter:\n")
    console.print(Panel.fit(f"[green]Text captured from clipboard:[/green]\n\n{current_paste}", title="✔ Text Captured",
                            border_style="green"))

    return current_paste