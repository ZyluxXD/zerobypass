#!/usr/bin/env python3
import asyncio
import pathlib
import subprocess
import sys
from typing import Optional

from playwright.async_api import async_playwright, Error, Playwright, BrowserContext
from rich.panel import Panel

from .config import console, args


class Playwrighter:
    def __init__(self):
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[BrowserContext] = None
        self._page_exists_lock = asyncio.Lock()

    async def start(self):
        await self._check_for_install()
        try:
            with console.status("[bold blue]Launching Playwright browser...", spinner="earth"):
                if args.browser_data_dir:
                    data_dir = args.browser_data_dir
                else:
                    data_dir = str(pathlib.Path.home() / ("." + pathlib.Path(__file__).parent.name))

                self.playwright = await async_playwright().start()
                self.browser = await self.playwright.chromium.launch_persistent_context(
                    user_data_dir=data_dir,
                    headless=False,
                    channel='chrome',
                    args=['--disable-blink-features=AutomationControlled']
                )
                await self.browser.grant_permissions(["clipboard-read", "clipboard-write"])
                # TODO fix: the handler doesnt work
                self.browser.on("close", self._user_closed_handler)
                await self._ensure_page_exists()
                # Keep Playwright alive until close() is called.
            console.print("[bold]✔ Playwright browser launched successfully[/bold]")
        except Exception as e:
            console.print(f"[red]Error initializing Playwright: {e}[/red]")
            await self.close()
            asyncio.get_event_loop().stop()

    async def navigate(self, url):
        page = await self.get_current_page()
        await page.goto(url)
        return page

    async def close(self):
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def _ensure_page_exists(self):
        if not self.browser.pages:
            await self.browser.new_page()

    async def get_current_page(self):
        """
        Returns the most recent page so typing happens on the tab the user is viewing.
        """
        async with self._page_exists_lock:
            await self._ensure_page_exists()

            # TODO fix: if the firs tab still exists it uses that instead
            page = next((p for p in reversed(self.browser.pages) if not p.is_closed()), None)

            if page is None:
                page = await self.browser.new_page()

            try:
                await page.bring_to_front()
            except Error:
                # If it was closed between checks, open a fresh page.
                page = await self.browser.new_page()

            return page

    @staticmethod
    async def _check_for_install():
        # Define the command
        cmd = [sys.executable, "-m", "playwright", "install", "--with-deps", "chrome"]

        try:
            # Start the status spinner
            with console.status("[bold blue]Verifying Playwright browser install...", spinner="earth"):
                # Use asyncio.subprocess.PIPE for async processes
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout_bytes, stderr_bytes = await process.communicate()

                stdout = stdout_bytes.decode('utf-8', errors='replace') if stdout_bytes else ""
                stderr = stderr_bytes.decode('utf-8', errors='replace') if stderr_bytes else ""

                if process.returncode != 0:
                    raise subprocess.CalledProcessError(process.returncode, cmd)

                # If there's output, print the success message
                if stdout.strip() or stderr.strip():
                    console.print("[bold green]✔ Playwright browsers installed successfully![/bold green]")
                # Use asyncio.sleep instead of time.sleep
                await asyncio.sleep(1)
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
        except Exception as e:
            console.print(
                Panel.fit(
                    f"[bold red]Verification Failed.[/bold red]\n"
                    f"{str(e)}",
                    title="Error",
                    border_style="red"
                )
            )

    @staticmethod
    async def _user_closed_handler(context):
        await context.close()
        console.print("[bold red]Browser window closed.[/bold red]")
        asyncio.Event().set()
