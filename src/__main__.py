#!/usr/bin/env python3
# Suppress Warning
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='stopit')
# ------------------------------------------------

from .algorithm import Algorithm
from .helpers import can_output_graphics, get_text, handle_disclaimer, wait_for_navigate
from .playwrighter import Playwrighter
# ------------------------------------------------
global pw
def main():
    global pw
    try:
        pw = None
        can_output_graphics()
        handle_disclaimer()
        captured_text, _ = get_text()
        pw = Playwrighter()
        wait_for_navigate()  # TODO: temp placeholder until the actual function is made. For the actual function, it should create the plan while waiting for the user to navigate in the browser. It should also have a cool ui.
        Algorithm(pw.current_page).type_text(captured_text)
    except KeyboardInterrupt:
        if pw:
            pw.close()
        
        



if __name__ == "__main__":
    main()
