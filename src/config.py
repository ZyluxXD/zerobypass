#!/usr/bin/env python3
import logging

from rich.console import Console

console = Console()

WINDOW_SECONDS = 5
LAST_SIG_TIME = 0.0

logging.getLogger("playwright").setLevel(logging.ERROR)  # TODO: verify if this actually does anything
