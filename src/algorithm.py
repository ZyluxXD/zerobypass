#!/usr/bin/env python3
import random
import string

class Algorithm:
    def __init__(
            self,
            page,
            *,
            min_delay: float = 0.035,
            max_delay: float = 0.1,
            punctuation_pause: tuple[float, float] = (0.25, 0.65),
            backtrack_chance: float = 0.015,
            steps_till_backtrack: tuple[int, int] = (2, 8)
    ):
        self.page = page
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.punctuation_pause = punctuation_pause
        self.backtrack_chance = backtrack_chance
        self.steps_till_backtrack = steps_till_backtrack
        self.typo_pending: tuple[
                               str, int, int, list] | None = None  # (correct_char, chars_until_correction, backtrack_count, typo_backlog)

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

                    # Check if we need to correct a pending typo
                    if self.typo_pending:
                        correct_char, chars_until_correction, backtrack_count, typo_backlog = self.typo_pending
                        if chars_until_correction <= 0:
                            self._correct_typo(keyboard, correct_char, backtrack_count, typo_backlog)
                            self.typo_pending = None
                        else:
                            typo_backlog.append(char)
                            self.typo_pending = (correct_char, chars_until_correction - 1, backtrack_count,
                                                 typo_backlog)
                    
                    delay = self._next_delay(char)

                    # Decide if we should make a typo on this character
                    if self._should_backtrack(idx, char) and not self.typo_pending:
                        # Create and type a typo instead of the correct character
                        typo_char = self._create_typo(char)
                        self._send_char(keyboard, typo_char)
                        self._sleep(delay)
                        # Schedule correction after 1-3 more characters
                        chars_until_correction = random.randint(*self.steps_till_backtrack)
                        self.typo_pending = (char, chars_until_correction, chars_until_correction + 1,
                                             [])  # I think it needs + 1 to work right
                    else:
                        # Type the character normally
                        self._send_char(keyboard, char)
                        self._sleep(delay)
                    
                    typed += 1
                    percent = (typed / total_chars) * 100 if total_chars else 100.0
                    status.update(f"[bold blue]Currently typing, progress: {percent:.2f}%[/bold blue]")

                # If there's still a pending typo at the end, correct it
                if self.typo_pending:
                    correct_char, chars_until_correction, backtrack_count, typo_backlog = self.typo_pending
                    self._correct_typo(keyboard, correct_char, backtrack_count, typo_backlog)
                    self.typo_pending = None
                    
            console.print("[bold green]✔ Finished typing[/bold green]")
        except KeyboardInterrupt:
            console.print("[yellow]Typing interrupted by user[/yellow]")
            pw.close()
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

        if idx < 3 or char.isspace():
            return False
        return random.random() < self.backtrack_chance

    def _short_pause(self) -> float:

        return random.uniform(self.min_delay * 0.5, self.min_delay * 1.5)

    def _correct_typo(self, keyboard, correct_char: str, backtrack: int, typo_backlog: list[str]):
        for _ in range(backtrack):
            keyboard.press("Backspace")
            self._sleep(self._short_pause() * 2.5)
        self._send_char(keyboard, correct_char)
        self._sleep(self._short_pause())
        for char in typo_backlog:
            delay = self._next_delay(char)
            self._send_char(keyboard, char)
            self._sleep(delay)

    @staticmethod
    def _create_typo(letter: str) -> str:
        if letter.isalpha():
            # Match case of original letter
            if letter.isupper():
                # Pick a different uppercase letter
                choices = [c for c in string.ascii_uppercase if c != letter]
                return random.choice(choices) if choices else random.choice(string.ascii_uppercase)
            else:
                # Pick a different lowercase letter
                choices = [c for c in string.ascii_lowercase if c != letter]
                return random.choice(choices) if choices else random.choice(string.ascii_lowercase)
        else:
            # For non-alphabetic characters, just return a random letter
            return random.choice(string.ascii_lowercase)
    @staticmethod
    def _sleep(duration: float):
        import time

        time.sleep(duration)
