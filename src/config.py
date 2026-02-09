#!/usr/bin/env python3
import logging

from rich.console import Console

console = Console()

WINDOW_SECONDS = 5
LAST_SIG_TIME = 0.0

logging.getLogger("playwright").setLevel(logging.ERROR)  # TODO: verify if this actually does anything

disclaimer = """

**Disclaimer — Research & Testing Only**

This project and its contents are provided strictly for research and testing purposes. They are not intended for educational use, including but not limited to classroom assignments, coursework, exams, tutorials, or any form of formal instruction or certification.

Do not use, submit, distribute, or present this code or its outputs as part of academic work or educational materials without explicit permission from the project maintainers and any affected parties. The authors and maintainers make no representations or warranties regarding suitability for educational use.

Use of this project is at your own risk. The authors and contributors accept no liability for any damages, legal consequences, or disciplinary actions that may arise from misuse, including presenting this work in an academic context where it is not allowed.

If you require a version of this project for legitimate educational purposes, please contact the maintainers to discuss appropriate licensing, attribution, and oversight.
"""
