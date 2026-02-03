#!/usr/bin/env python3
# --------------------IMPORTS-----------------------
# ------------MISC------------
# type: ignore
import logging
import os
import subprocess
import sys
import threading
import time

import klembord
# ----------PLAYWRITE-----------
import playwright.sync_api
from _pytest import pathlib
# ------------RICH------------
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

# --------------------CONFIG------------------------
console = Console()
WINDOW_SECONDS = 5
LAST_SIG_TIME = 0.0
logging.getLogger("playwright").setLevel(logging.ERROR)
logging.basicConfig(level=logging.ERROR)
# --------------------------------------------------
