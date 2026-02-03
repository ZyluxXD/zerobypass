import os
import pathlib
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright
from rich.panel import Panel

from config import console


class Playwrighter:
    def __init__(self):
        self._check_for_install()
        try:
            with console.status("[bold blue]Launching Playwright browser...", spinner="earth"):
                data_dir = os.path.join(os.path.expanduser("~"), "." + pathlib.Path(__file__).parent.parent.name)
                self.playwright = sync_playwright().start()
                self.context = self.playwright.chromium.launch_persistent_context(user_data_dir=data_dir,
                                                                                  headless=False)
                # TODO fix: the handler doesnt work
                self.context.on("close", self._user_closed_handler)
                self.page = self.context.new_page()
                self.page.goto("https://docs.google.com/")
            self.page.pause()
        except Exception as e:
            console.print(f"[red]Error initializing Playwright: {e}[/red]")
            sys.exit(1)

    def navigate(self, url):
        self.page.goto(url)

    def close(self):
        self.context.close()
        self.playwright.stop()

    @staticmethod
    def _check_for_install():
        # Define the command
        cmd = [sys.executable, "-m", "playwright", "install", "--with-deps", "chromium"]

        try:
            # Start the status spinner
            with console.status("[bold blue]Verifying Playwright browser install...", spinner="earth"):
                process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, cmd)

                # If there's output, print the success message
                if stdout.strip() or stderr.strip():
                    console.print("[bold green]✔ Playwright browsers installed successfully![/bold green]")
                time.sleep(1)
            console.clear()
        except subprocess.CalledProcessError:
            console.print(
                Panel.fit(
                    "[bold red]Installation Failed.[/bold red]\n"
                    "Make sure you have run: [bold cyan]pip install playwright[/bold cyan]",
                    title="Error",
                    border_style="red"
                )
            )

    @staticmethod
    def _user_closed_handler(context):
        context.close()
        console.print("[bold red]Browser context closed.[/bold red]")
        sys.exit(1)
