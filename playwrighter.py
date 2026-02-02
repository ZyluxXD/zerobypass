from __init__ import *

class Playwrighter:
    def __init__(self):
        self._checkForInstall()
        try:
            self.playwright = playwright.sync_api.sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=False)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
        except Exception as e:
            console.print(f"[red]Error initializing Playwright: {e}[/red]")
            sys.exit(1)

    def navigate(self, url):
        self.page.goto(url)

    def close(self):
        self.context.close()
        self.browser.close()
        self.playwright.stop()

    def _checkForInstall(self):
        # Define the command
        cmd = [sys.executable, "-m", "playwright", "install"]
        
        try:
            # Start the status spinner
            with console.status("[bold blue]Installing Playwright browsers...", spinner="earth"):
                # We use capture_output=False here so the user can see 
                # the actual download progress if they want, 
                # or keep it True for a silent install.
                subprocess.run(cmd, check=True)
                
            console.print("[bold green]✔ Playwright browsers installed successfully![/bold green]")

        except subprocess.CalledProcessError:
            console.print(
                Panel.fit(
                    "[bold red]Installation Failed.[/bold red]\n"
                    "Make sure you have run: [bold cyan]pip install playwright[/bold cyan]",
                    title="Error",
                    border_style="red"
                )
            )