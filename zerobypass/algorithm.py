#!/usr/bin/env python3
import asyncio
import random
import string
from dataclasses import dataclass
from typing import Optional, List, Tuple

from rich.prompt import Prompt

from .config import console
from .helpers import listen_for_pause, wait_for_navigate


# --- Configuration ---
@dataclass
class Config:
    """Holds all tunable parameters for the typing behavior."""
    min_delay: float = 0.035
    max_delay: float = 0.1
    punctuation_pause: Tuple[float, float] = (0.25, 0.65)
    backtrack_chance: float = 0.015
    steps_till_backtrack: Tuple[int, int] = (2, 10)
    fatigue_scale = 1.01  # 1% slowdown every interval
    fatigue_interval = 50
    # feature config
    enable_typos: bool = True
    enable_jitter: bool = True
    enable_fatigue: bool = True


class Modules:
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.timer = Delay(self)
        self.typos = Typo(self)
        # Register modules that need to hook into the typing lifecycle
        self.registry = [self.typos]
        self.typed_count: int = 0

    def __getattr__(self, name):
        return getattr(self.config, name)

    async def process_lifecycle(self, keyboard, char: str, index: int) -> str:
        # handling pre-type logic
        for mod in self.registry:
            if hasattr(mod, 'pre_char'):
                await mod.pre_char(keyboard)
            if hasattr(mod, 'tick'):
                mod.tick(char)

        # handling char transformations
        final_char = char
        for mod in self.registry:
            if hasattr(mod, 'on_char'):
                final_char = mod.on_char(final_char, index)

        return final_char

    async def post_lifecycle(self, keyboard) -> None:
        for mod in self.registry:
            if hasattr(mod, 'postprocess'):
                await mod.postprocess(keyboard)

    async def send_char(self, keyboard, char: str, delay=None):
        if char == "\n":
            await keyboard.press("Enter")
        else:
            await keyboard.insert_text(char)

        if delay is not None:
            await self.timer.sleep(delay)


# --- Delay Logic  ---
class Delay:
    """math"""

    def __init__(self, mod: Modules):
        self.mod = mod

    def __getattr__(self, name):
        return getattr(self.mod.config, name)

    def get_delay(self, char: str) -> float:
        multiplier = self.get_fatigue_multiplier()
        if not self.enable_jitter:
            return self.min_delay * multiplier

        delay = random.uniform(self.min_delay, self.max_delay)

        # Longer pauses for punctuation
        if char in {".", "?", "!", ",", ";", ":"}:
            delay += random.uniform(*self.punctuation_pause)
        elif char == "\n":
            delay += random.uniform(*self.punctuation_pause)
        elif char == " ":
            delay += random.uniform(0, 0.08)
        return delay * multiplier

    def get_short_pause(self) -> float:
        return random.uniform(self.min_delay * 0.5, self.max_delay * 1.5)

    def get_fatigue_multiplier(self) -> float:
        if not self.mod.config.enable_fatigue:
            return 1.0
        # For every 50 chars, increase delay by 1%
        level = self.mod.typed_count // self.fatigue_interval
        return self.fatigue_scale ** level

    @staticmethod
    async def sleep(duration: float):
        await asyncio.sleep(duration)


# --- Module 3: Typo Logic (The "Brain" of errors) ---
class Typo:
    """typos"""

    def __init__(self, mod: Modules):
        self.mod = mod
        # State tracking
        self.pending_correction: Optional[str] = None
        self.steps_remaining: int = 0
        self.backtrack_amount: int = 0
        self.backlog: List[str] = []

    def __getattr__(self, name):
        """Map missing attributes to the hub/config."""
        return getattr(self.mod, name)

    @property
    def is_correction_pending(self) -> bool:
        return self.pending_correction is not None

    def should_start_typo(self, char: str, index: int) -> bool:
        """Decides if a new typo sequence should start."""
        if not self.enable_typos or self.is_correction_pending:
            return False

        if index < 3 or char.isspace():
            return False

        return random.random() < self.backtrack_chance

    def generate_typo_char(self, char: str, register=True) -> str:
        if register:
            self.register_typo(char)

        low_char = char.lower()
        if low_char in self.QWERTY:
            neighbors = self.QWERTY[low_char]
            pool = [n.upper() if char.isupper() else n for n in neighbors]
            return random.choice(pool)
        else:
            pool = [c for c in string.ascii_lowercase if c != low_char]
            typo = random.choice(pool)
            return typo.upper() if char.isupper() else typo

    def register_typo(self, correct_char: str):
        """Sets up the state machine to correct this typo later."""
        steps = random.randint(*self.steps_till_backtrack)

        self.pending_correction = correct_char
        self.steps_remaining = steps
        self.backtrack_amount = steps + 1
        self.backlog = []

    async def perform_correction(self, keyboard):
        short_pause = self.timer.get_short_pause()
        for _ in range(self.backtrack_amount):
            await keyboard.press("Backspace")
            await self.timer.sleep(short_pause * 2.5)

        await self.send_char(keyboard, self.pending_correction, short_pause)

        for buffered_char in self.backlog:
            delay = self.timer.get_delay(buffered_char)
            await self.send_char(keyboard, buffered_char, delay)
        self.reset()

    def tick(self, char: str):
        """Decrements the counter until correction."""
        if self.is_correction_pending:
            self.backlog.append(char)
            self.steps_remaining -= 1

    def reset(self):
        """Clears state after a fix."""
        self.pending_correction = None
        self.steps_remaining = 0
        self.backtrack_amount = 0
        self.backlog = []

    async def pre_char(self, keyboard):
        """Executes the physical backspacing and re-typing."""
        if self.is_correction_pending and self.steps_remaining <= 0:
            await self.perform_correction(keyboard)

    def on_char(self, char: str, index: int) -> str:
        if self.should_start_typo(char, index):
            return self.generate_typo_char(char)
        return char

    async def postprocess(self, keyboard):
        if self.is_correction_pending:
            await self.perform_correction(keyboard)

    QWERTY = {
        # Number Row
        '`': ['1', 'q'], '1': ['`', '2', 'q', 'w'], '2': ['1', '3', 'q', 'w', 'e'],
        '3': ['2', '4', 'w', 'e', 'r'], '4': ['3', '5', 'e', 'r', 't'],
        '5': ['4', '6', 'r', 't', 'y'], '6': ['5', '7', 't', 'y', 'u'],
        '7': ['6', '8', 'y', 'u', 'i'], '8': ['7', '9', 'u', 'i', 'o'],
        '9': ['8', '0', 'i', 'o', 'p'], '0': ['9', '-', 'o', 'p', '['],
        '-': ['0', '=', 'p', '[', ']'], '=': ['-', '[', ']'],
        # Top Row
        'q': ['`', '1', '2', 'w', 'a', 's'], 'w': ['1', '2', '3', 'q', 'e', 'a', 's', 'd'],
        'e': ['2', '3', '4', 'w', 'r', 's', 'd', 'f'], 'r': ['3', '4', '5', 'e', 't', 'd', 'f', 'g'],
        't': ['4', '5', '6', 'r', 'y', 'f', 'g', 'h'], 'y': ['5', '6', '7', 't', 'u', 'g', 'h', 'j'],
        'u': ['6', '7', '8', 'y', 'i', 'h', 'j', 'k'], 'i': ['7', '8', '9', 'u', 'o', 'j', 'k', 'l'],
        'o': ['8', '9', '0', 'i', 'p', 'k', 'l', ';'], 'p': ['9', '0', '-', 'o', '[', 'l', ';', "'"],
        '[': ['0', '-', '=', 'p', ']', ';', "'"], ']': ['-', '=', '[', '\\', "'"], '\\': [']'],
        # Home Row
        'a': ['q', 'w', 's', 'z', 'x'], 's': ['q', 'w', 'e', 'a', 'd', 'z', 'x', 'c'],
        'd': ['w', 'e', 'r', 's', 'f', 'x', 'c', 'v'], 'f': ['e', 'r', 't', 'd', 'g', 'c', 'v', 'b'],
        'g': ['r', 't', 'y', 'f', 'h', 'v', 'b', 'n'], 'h': ['t', 'y', 'u', 'g', 'j', 'b', 'n', 'm'],
        'j': ['y', 'u', 'i', 'h', 'k', 'n', 'm', ','], 'k': ['u', 'i', 'o', 'j', 'l', 'm', ',', '.'],
        'l': ['i', 'o', 'p', 'k', ';', ',', '.', '/'], ';': ['o', 'p', '[', 'l', "'", '.', '/'],
        "'": ['p', '[', ']', ';', '/'],
        # Bottom Row
        'z': ['a', 's', 'x'], 'x': ['a', 's', 'd', 'z', 'c'], 'c': ['s', 'd', 'f', 'x', 'v'],
        'v': ['d', 'f', 'g', 'c', 'b'], 'b': ['f', 'g', 'h', 'v', 'n'], 'n': ['g', 'h', 'j', 'b', 'm'],
        'm': ['h', 'j', 'k', 'n', ','], ',': ['j', 'k', 'l', 'm', '.'], '.': ['k', 'l', ';', ',', '/'],
        '/': ['l', ';', "'", '.']
    }


# --- orchestrator class ---
class Algorithm:
    def __init__(self, page, config: Optional[Config] = None):
        self.mod = Modules(config)
        self.page = page
        self._is_paused = asyncio.Event()
        self._is_paused.set()
        self._restart_requested = False
        self.pause_requested = False
        self.pause_task = None

    def __getattr__(self, name):
        return getattr(self.mod, name)

    async def _handle_pause_prompt(self, status):
        self.pause_requested = False
        status.stop()
        console.clear()
        console.print("\n" + "─" * 30)

        try:
            Prompt.ask(
                "[bold yellow]PAUSED[/bold yellow]\n"
                "• Press [bold green]Enter[/bold green] to resume\n"
                "• Press [bold red]Ctrl+C[/bold red] to restart",
                password=True
            )
            console.print("[green]▶ Resuming...[/green]")
            if self.pause_task:
                self.pause_task.cancel()
        except KeyboardInterrupt:
            self._restart_requested = True
            console.print("\n[bold magenta]↺ Restarting...[/bold magenta]")
            await wait_for_navigate()
        finally:
            self.pause_task = asyncio.create_task(listen_for_pause(self))
            console.clear()
        if not self._restart_requested:
            status.start()
            console.print("─" * 30 + "\n")

    async def type_text(self, text: str):
        self.pause_task = asyncio.create_task(listen_for_pause(self))

        while True:
            self._restart_requested = False
            self.typos.reset()
            total_chars = len(text)
            self.mod.typed_count = 0
            try:
                msg = "[bold blue]Currently typing, progress: 0.00%. Press enter to pause.[/bold blue]"
                with console.status(msg, spinner="bouncingBall") as status:

                    for idx, raw_char in enumerate(text):
                        if self.pause_requested or self._restart_requested:
                            await self._handle_pause_prompt(status)

                        if self._restart_requested:
                            break

                        await self._is_paused.wait()
                        if raw_char == "\r": continue
                        char = "\n" if raw_char == "\n" else raw_char

                        # lifecycle call
                        char_to_type = await self.mod.process_lifecycle(self.page.keyboard, char, idx)

                        # Calculate delay based on the original intended character
                        delay = self.timer.get_delay(char)

                        # Send the final character
                        await self.mod.send_char(self.page.keyboard, char_to_type, delay)

                        self.mod.typed_count += 1
                        percent = (self.mod.typed_count / total_chars) * 100
                        status.update(f"[bold blue]Currently typing, progress: {percent:.2f}%.[/bold blue]")

                if not self._restart_requested:
                    await self.mod.post_lifecycle(self.page.keyboard)
                    console.print("[bold green]✔ Finished typing[/bold green]")
                    if self.pause_task: self.pause_task.cancel()
                    break

            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                raise

    def request_pause(self):
        self.pause_requested = True
