#!/usr/bin/env python3

class Algorithm:
    def __init__(
            self,
            page,
            *,
            min_delay: float = 0.035,
            max_delay: float = 0.1,
            punctuation_pause: tuple[float, float] = (0.25, 0.65),
            backtrack_chance: float = 0.015,
    ):
        self.page = page
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.punctuation_pause = punctuation_pause
        self.backtrack_chance = backtrack_chance

    def type_text(self, text: str):
        from .config import console  # lazy import to avoid circulars
        from .__main__ import pw
        keyboard = self.page.keyboard
        total_chars = sum(1 for c in text if c != "\r")
        typed = 0
        try:
            with console.status(f"[bold blue]Currently typing, progress: {0:.2f}%[/bold blue]",
                                spinner="bouncingBall") as status:
                for idx, raw_char in enumerate(text):
                    if raw_char == "\r":
                        continue  # normalize Windows newlines

                    char = "\n" if raw_char == "\n" else raw_char
                    delay = self._next_delay(char)

                    if self._should_backtrack(idx, char):
                        keyboard.press("Backspace")
                        self._sleep(self._short_pause())

                    self._send_char(keyboard, char)
                    self._sleep(delay)
                    typed += 1
                    percent = (typed / total_chars) * 100 if total_chars else 100.0
                    status.update(f"[bold blue]Currently typing, progress: {percent:.2f}%[/bold blue]")
            console.print("[bold green]✔ Finished typing[/bold green]")
        except KeyboardInterrupt:
            console.print("[yellow]Typing interrupted by user[/yellow]")
            pw.stop()
            return

        except Exception as exc:
            console.print(f"[red]Typing failed: {exc}[/red]")
            raise

    @staticmethod
    def _send_char(keyboard, char: str):
        if char == "\n":
            keyboard.press("Enter")
        else:
            keyboard.insert_text(char)

    def _next_delay(self, char: str) -> float:
        # Base delay with jitter.
        import random

        delay = random.uniform(self.min_delay, self.max_delay)

        # Slightly longer after punctuation or newlines.
        if char in {".", "?", "!", ",", ";", ":"}:
            delay += random.uniform(*self.punctuation_pause)
        elif char == "\n":
            delay += random.uniform(*self.punctuation_pause)
        elif char == " ":
            # Rare micro-pause between words.
            delay += random.uniform(0, 0.08)

        return delay

    def _should_backtrack(self, idx: int, char: str) -> bool:
        # Do not backtrack immediately at the start or on whitespace/newlines.
        import random

        if idx < 3 or char.isspace():
            return False
        return random.random() < self.backtrack_chance

    def _short_pause(self) -> float:
        import random

        return random.uniform(self.min_delay * 0.5, self.min_delay * 1.5)

    @staticmethod
    def _sleep(duration: float):
        import time

        time.sleep(duration)
