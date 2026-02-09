#!/usr/bin/env python3
import os
import pathlib
import subprocess
import sys
import time

from playwright.sync_api import sync_playwright
from rich.panel import Panel

from .config import console


class Playwrighter:
    def __init__(self):
        self._check_for_install()
        try:
            with console.status("[bold blue]Launching Playwright browser...", spinner="earth"):
                data_dir = os.path.join(os.path.expanduser("~"), "." + pathlib.Path(__file__).parent.parent.name)
                self.playwright = sync_playwright().start()
                self.browser = self.playwright.chromium.launch_persistent_context( # TODO fix: launch with user existing profile to evade bot detection
                    user_data_dir=data_dir,
                    headless=False
                )
                # TODO fix: the handler doesnt work
                self.browser.on("close", self._user_closed_handler)
                self._ensure_page_exists()
                # this would normally close immediately; however, there is more code executing in main.py so it doesn't close
            console.print("[bold]✔ Playwright browser launched successfully[/bold]")
        except Exception as e:
            console.print(f"[red]Error initializing Playwright: {e}[/red]")
            sys.exit(1)

    def navigate(self, url):
        page = self.current_page
        page.goto(url)
        return page

    def close(self):
        self.browser.close()
        self.playwright.stop()

    def _ensure_page_exists(self):
        if not self.browser.pages:
            self.browser.new_page()

    @property
    def current_page(self):
        """
        Returns the most recent page so typing happens on the tab the user is viewing.
        """
        self._ensure_page_exists()

        # Prefer the most recent non-closed page; fall back to a new one.
        # TODO fix: if the firs tab still exists it uses that instead
        page = next((p for p in reversed(self.browser.pages) if not p.is_closed()), None)
        if page is None:
            page = self.browser.new_page()

        try:
            page.bring_to_front()
        except Exception:
            # If it was closed between checks, open a fresh page.
            page = self.browser.new_page()

        return page

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
        console.print("[bold red]Browser window closed.[/bold red]")
        sys.exit(1)
