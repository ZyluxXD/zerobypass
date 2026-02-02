#!/usr/bin/env python3
# --------------------IMPORTS-----------------------
# ------------MISC------------
import sys
import time
import os
import threading
import subprocess
import logging
# ------------RICH------------
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.markdown import Markdown
# ----------PLAYWRITE-----------
import playwright.sync_api

# --------------------CONFIG------------------------
console = Console()
WINDOW_SECONDS = 5
LAST_SIG_TIME = 0.0
logging.getLogger("playwright").setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)
# --------------------------------------------------
