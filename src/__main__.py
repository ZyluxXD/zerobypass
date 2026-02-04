#!/usr/bin/env python3
from helpers import can_output_graphics, get_text, handle_disclaimer
from playwrighter import Playwrighter
# ------------------------------------------------


def main():
    can_output_graphics()
    handle_disclaimer()
    get_text()
    pw = Playwrighter()
    get_text()  # TODO: temp placeholder until the actual function is made. For the actual function, it should create the plan while waiting for the user to navigate in the browser. It should also have a cool ui.


if __name__ == "__main__":
    main()
