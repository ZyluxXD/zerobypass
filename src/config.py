import logging

from rich.console import Console

console = Console()

WINDOW_SECONDS = 5
LAST_SIG_TIME = 0.0

logging.getLogger("playwright").setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)
