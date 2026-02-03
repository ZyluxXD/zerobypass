#!/usr/bin/env python3
from helpers import get_text, handle_disclaimer
from playwrighter import Playwrighter
# ------------------------------------------------


def main():
    handle_disclaimer()
    get_text()
    pw = Playwrighter()


if __name__ == "__main__":
    main()
