#!/usr/bin/env python3
from helpers import can_output_graphics, get_text, handle_disclaimer
from playwrighter import Playwrighter
# ------------------------------------------------


def main():
    can_output_graphics()
    handle_disclaimer()
    get_text()
    pw = Playwrighter()


if __name__ == "__main__":
    main()
