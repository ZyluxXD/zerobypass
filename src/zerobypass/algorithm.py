#!/usr/bin/env python3
import random
import string
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
    steps_till_backtrack: Tuple[int, int] = (2, 10)

    # feature config
    enable_typos: bool = True
    enable_jitter: bool = True


# --- Delay Logic  ---
class Delay:
    """math"""

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
    """typos"""

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
        # register if needed
        if register:
            self.register_typo(char)

        # lower the char for it to work
        low_char = char.lower()

        if low_char in self.QWERTY:
            neighbors = self.QWERTY[low_char]

            # list comprehension
            pool = [n.upper() if char.isupper() else n for n in neighbors]

            return random.choice(pool)

        # fallback
        else:
            pool = [c for c in string.ascii_lowercase if c != low_char]
            typo = random.choice(pool)
            return typo.upper() if char.isupper() else typo

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

    QWERTY = {
        # Number Row
        '`': ['1', 'q'],
        '1': ['`', '2', 'q', 'w'],
        '2': ['1', '3', 'q', 'w', 'e'],
        '3': ['2', '4', 'w', 'e', 'r'],
        '4': ['3', '5', 'e', 'r', 't'],
        '5': ['4', '6', 'r', 't', 'y'],
        '6': ['5', '7', 't', 'y', 'u'],
        '7': ['6', '8', 'y', 'u', 'i'],
        '8': ['7', '9', 'u', 'i', 'o'],
        '9': ['8', '0', 'i', 'o', 'p'],
        '0': ['9', '-', 'o', 'p', '['],
        '-': ['0', '=', 'p', '[', ']'],
        '=': ['-', '[', ']'],

        # Top Row
        'q': ['`', '1', '2', 'w', 'a', 's'],
        'w': ['1', '2', '3', 'q', 'e', 'a', 's', 'd'],
        'e': ['2', '3', '4', 'w', 'r', 's', 'd', 'f'],
        'r': ['3', '4', '5', 'e', 't', 'd', 'f', 'g'],
        't': ['4', '5', '6', 'r', 'y', 'f', 'g', 'h'],
        'y': ['5', '6', '7', 't', 'u', 'g', 'h', 'j'],
        'u': ['6', '7', '8', 'y', 'i', 'h', 'j', 'k'],
        'i': ['7', '8', '9', 'u', 'o', 'j', 'k', 'l'],
        'o': ['8', '9', '0', 'i', 'p', 'k', 'l', ';'],
        'p': ['9', '0', '-', 'o', '[', 'l', ';', "'"],
        '[': ['0', '-', '=', 'p', ']', ';', "'"],
        ']': ['-', '=', '[', '\\', "'"],
        '\\': [']'],

        # Home Row
        'a': ['q', 'w', 's', 'z', 'x'],
        's': ['q', 'w', 'e', 'a', 'd', 'z', 'x', 'c'],
        'd': ['w', 'e', 'r', 's', 'f', 'x', 'c', 'v'],
        'f': ['e', 'r', 't', 'd', 'g', 'c', 'v', 'b'],
        'g': ['r', 't', 'y', 'f', 'h', 'v', 'b', 'n'],
        'h': ['t', 'y', 'u', 'g', 'j', 'b', 'n', 'm'],
        'j': ['y', 'u', 'i', 'h', 'k', 'n', 'm', ','],
        'k': ['u', 'i', 'o', 'j', 'l', 'm', ',', '.'],
        'l': ['i', 'o', 'p', 'k', ';', ',', '.', '/'],
        ';': ['o', 'p', '[', 'l', "'", '.', '/'],
        "'": ['p', '[', ']', ';', '/'],

        # Bottom Row
        'z': ['a', 's', 'x'],
        'x': ['a', 's', 'd', 'z', 'c'],
        'c': ['s', 'd', 'f', 'x', 'v'],
        'v': ['d', 'f', 'g', 'c', 'b'],
        'b': ['f', 'g', 'h', 'v', 'n'],
        'n': ['g', 'h', 'j', 'b', 'm'],
        'm': ['h', 'j', 'k', 'n', ','],
        ',': ['j', 'k', 'l', 'm', '.'],
        '.': ['k', 'l', ';', ',', '/'],
        '/': ['l', ';', "'", '.']
    }


# --- orchestrator class ---
class Algorithm:
    # TODO add: add a way to use rich text
    def __init__(self, page, config: Optional[Config] = None):
        self.page = page
        self.config = config or Config()
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

        except KeyboardInterrupt:
            console.print("[yellow]Typing interrupted[/yellow]")
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
