from __init__ import *
# ------------------------------------------------
def canOutputGraphics():
    # This doesnt work :(
    if not any(var in os.environ for var in ['DISPLAY', 'WAYLAND_DISPLAY']):
        console.print("[red]No graphical display detected. This needs graphical output to work.[/red]")
        sys.exit(0)


def handleDisclaimer():
    filepath = os.path.join(os.path.dirname(__file__), 'DISCLAIMER.md')
    with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    disclaimer = Markdown(content) 
    panel = Panel(disclaimer, title="⚠ Disclaimer ⚠", border_style="red")
    console.print(panel)
    accepted = Confirm.ask("Do you accept this disclaimer?", choices=["y", "n"])

    if accepted:
        console.clear()
    else:
        console.print(f"[yellow]Not accepted. The application will exit now.[/yellow]")
        sys.exit(0)

def getText():
     return Prompt.ask("Enter the content to use for the bypass", console=console)