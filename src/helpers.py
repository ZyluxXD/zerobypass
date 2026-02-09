#!/usr/bin/env python3
import sys
import time

import klembord
from Xlib import display, error
from rich.markdown import Markdown
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from .config import console, disclaimer


# ------------------------------------------------
def can_output_graphics():
    if sys.platform.startswith("win"):
        # X11 displays are not available on Windows by default, so skip checking
        # If they don't have a display for some reason IDK why they would download this on a headless Windows environment lol
        return True
    try:
        display.Display()
    except (error.DisplayConnectionError, error.DisplayNameError):
        with console.status("[red]Unable to connect to graphical display. Press [bold]Enter[/bold] to continue anyway. Press [bold]CTRL-C[/bold] to exit.[/red]", spinner="star"):
            Prompt.ask(password=True)
    return True

def handle_disclaimer():
    content = Markdown(disclaimer)
    panel = Panel(content, title="Disclaimer", border_style="red")
    console.print(panel)
    accepted = Confirm.ask("Do you accept this disclaimer?", choices=["y", "n"])

    if accepted:
        console.clear()
    else:
        console.print("[yellow]Not accepted. The application will exit now.[/yellow]")
        sys.exit(0)


# I cooked on this one :)
def get_text():
    while True:

        try:
            with console.status("[bold]Copy[/bold] the text you want to use onto your clipboard [dim](CTRL-C)[/dim]",
                            spinner="bouncingBar"):
                klembord.clear()  # avoid not copying due to copied content matching newly copied content
                last_paste = klembord.get_with_rich_text()
                while True:
                    current_paste = klembord.get_with_rich_text()
                    if current_paste != last_paste:
                        break
                    time.sleep(0.1)  # small delay because yes
        except (error.DisplayConnectionError, error.DisplayNameError):
            console.print("[yellow]Clipboard access failed. Falling back to manual input.[/yellow]")
            current_paste = (console.input("Paste text here and press Enter:\n"), "")
        # Escape clipboard text to avoid Rich markup errors if user text contains markup-like tags.
        # not to be confused with the library Rich (I mean Rich text, HTML, etc.)
        safe_plain = escape(current_paste[0]).strip()
        safe_rich = escape(current_paste[1].strip()) if current_paste[1] else None
        # show a 1/4 preview of the text in rich HTML format
        rich_preview_len = len(safe_plain) // 4
        preview = f"{safe_plain}{'\n [dim]' + safe_rich[:rich_preview_len] + '...[/dim]' if safe_rich else ''}"
        console.print(Panel.fit(preview, title="Text Captured", border_style="green"))
        confirm = Confirm.ask(f"Do you wish to continue with this capture or re-capture?", default=True,
                              choices=["y", "n"])
        if confirm:
            break

    return current_paste

def wait_for_navigate():
    console.print("[bold]Now navigate to the page you want to use, in the Playwright browser.[/bold]")
    console.print("[dim]Click into the input where you want the text to appear, then return here.[/dim]")
    with console.status("[bold] Waiting for navigation and focus... [/bold] [dim]Press Enter to start typing.[/dim]",
                        spinner="simpleDotsScrolling"):
        Prompt.ask(password=True)  # hack for entering


def wait_till_exit():
    with console.status(
            "[bold] The script will continue to run to ensure the browser doesn't close. Press enter to exit.[/bold]",
            spinner="hamburger"):
        Prompt.ask(password=True)
