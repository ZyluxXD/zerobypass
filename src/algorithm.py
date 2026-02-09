#!/usr/bin/env python3
import random
import string
import sys
import time
from dataclasses import dataclass
from typing import Optional, List, Tuple

from .config import console


# --- Configuration ---
@dataclass
class Config:
    """Holds all tunable parameters for the typing behavior."""
    min_delay: float = 0.035
    max_delay: float = 0.1
    punctuation_pause: Tuple[float, float] = (0.25, 0.65)
    backtrack_chance: float = 0.015
    steps_till_backtrack: Tuple[int, int] = (2, 8)

    # New: Allow enabling/disabling features easily
    enable_typos: bool = True
    enable_jitter: bool = True


# --- Delay Logic  ---
class Delay:
    """Handles the mathematics of human-like pauses."""

    def __init__(self, config: Config):
        self.config = config

    def get_delay(self, char: str) -> float:
        if not self.config.enable_jitter:
            return self.config.min_delay

        delay = random.uniform(self.config.min_delay, self.config.max_delay)

        # Longer pauses for punctuation
        if char in {".", "?", "!", ",", ";", ":"}:
            delay += random.uniform(*self.config.punctuation_pause)
        elif char == "\n":
            delay += random.uniform(*self.config.punctuation_pause)
        elif char == " ":
            delay += random.uniform(0, 0.08)

        return delay

    def get_short_pause(self) -> float:
        return random.uniform(self.config.min_delay * 0.5, self.config.min_delay * 1.5)

    @staticmethod
    def sleep(duration: float):
        time.sleep(duration)


# --- Module 3: Typo Logic (The "Brain" of errors) ---
class Typo:
    """
    Manages the state of pending typos.
    Decides when to make a mistake and how to fix it.
    """

    def __init__(self, config: Config):
        self.config = config
        # State tracking
        self.pending_correction: Optional[str] = None  # The char we SHOULD have typed
        self.steps_remaining: int = 0
        self.backtrack_amount: int = 0
        self.backlog: List[str] = []

    @property
    def is_correction_pending(self) -> bool:
        return self.pending_correction is not None

    def should_start_typo(self, char: str, index: int) -> bool:
        """Decides if a new typo sequence should start."""
        if not self.config.enable_typos or self.is_correction_pending:
            return False
        # Don't typo on spaces, newlines, or very early in the text
        if index < 3 or char.isspace():
            return False
        return random.random() < self.config.backtrack_chance

    def generate_typo_char(self, char: str, register=True) -> str:
        """Returns a plausible wrong character."""
        # TODO: Use QWERTY proximity here instead of random
        if register:
            self.register_typo(char)
        if char.isalpha():
            if char.isupper():
                pool = [c for c in string.ascii_uppercase if c != char]
                return random.choice(pool)
            else:
                pool = [c for c in string.ascii_lowercase if c != char]
                return random.choice(pool)
        return random.choice(string.ascii_lowercase)

    def register_typo(self, correct_char: str):
        """Sets up the state machine to correct this typo later."""
        steps = random.randint(*self.config.steps_till_backtrack)
        self.pending_correction = correct_char
        self.steps_remaining = steps
        self.backtrack_amount = steps + 1
        self.backlog = []

    def tick(self, char: str):
        """Decrements the counter until correction."""
        if self.is_correction_pending:
            self.backlog.append(char)
            self.steps_remaining -= 1

    def ready_to_fix(self) -> bool:
        return self.is_correction_pending and self.steps_remaining <= 0

    def reset(self):
        """Clears state after a fix."""
        self.pending_correction = None
        self.steps_remaining = 0
        self.backtrack_amount = 0
        self.backlog = []


# --- orchestrator class ---
class Algorithm:
    # TODO add: add a way to use rich text
    def __init__(self, page, config: Optional[Config] = None):
        self.page = page
        self.config = config or Config()
        # Composition: Use the specialized managers
        self.timer = Delay(self.config)
        self.typos = Typo(self.config)

    def type_text(self, text: str):
        keyboard = self.page.keyboard
        total_chars = len(text)
        typed_count = 0

        try:
            with console.status(f"[bold blue]Currently typing, progress: {0:.2f}%[bold blue]",
                                spinner="bouncingBall") as status:

                for idx, raw_char in enumerate(text):
                    if raw_char == "\r": continue
                    char = "\n" if raw_char == "\n" else raw_char

                    # 1. Check if we need to fix a previous error
                    if self.typos.ready_to_fix():
                        self._perform_correction(keyboard)
                    elif self.typos.is_correction_pending:
                        self.typos.tick(char)

                    # 2. Calculate delay for this specific char
                    delay = self.timer.get_delay(char)

                    # 3. Decide: Type correctly or make a mistake?
                    if self.typos.should_start_typo(char, idx):
                        # make a typo & register (gen typo auto registers)
                        typo_char = self.typos.generate_typo_char(char)
                        self._send_char(keyboard, typo_char, delay)
                    else:
                        # Normal typing
                        self._send_char(keyboard, char, delay)

                    # Update UI
                    typed_count += 1
                    percent = (typed_count / total_chars) * 100
                    status.update(f"[bold blue]Currently typing, progress: {percent:.2f}%[/bold blue]")

                # Final cleanup: If a typo is still pending at the end of the string
                if self.typos.is_correction_pending:
                    self._perform_correction(keyboard)

            console.print("[bold green]✔ Finished typing[/bold green]")
            # TODO add: add a better finished prompt with statistics like time
        except KeyboardInterrupt:
            console.print("[yellow]Typing interrupted[/yellow]")
            sys.exit(1)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
            raise

    def _perform_correction(self, keyboard):
        """Executes the physical backspacing and re-typing."""
        # Backspace
        for _ in range(self.typos.backtrack_amount):
            keyboard.press("Backspace")
            self.timer.sleep(self.timer.get_short_pause() * 2.5)

        # Type the character that was originally missed
        self._send_char(keyboard, self.typos.pending_correction, self.timer.get_short_pause())

        # Re-type the buffer (characters typed while we didn't notice the error)
        for buffered_char in self.typos.backlog:
            delay = self.timer.get_delay(buffered_char)
            self._send_char(keyboard, buffered_char, delay)

        self.typos.reset()

    def _send_char(self, keyboard, char: str, delay=None):
        if char == "\n":
            keyboard.press("Enter")
        else:
            keyboard.insert_text(char)
        if delay is not None:
            self.timer.sleep(delay)
