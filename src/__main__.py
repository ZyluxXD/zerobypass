#!/usr/bin/env python3
# Suppress Warning
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='stopit')
# ------------------------------------------------

from .helpers import can_output_graphics, get_text, handle_disclaimer, wait_for_navigate
from .playwrighter import Playwrighter

# ------------------------------------------------
def main():
    pw = None
    try:
        can_output_graphics()
        handle_disclaimer()
        wait_for_navigate()
        get_text()
        pw = Playwrighter()
        get_text()  # TODO: temp placeholder until the actual function is made. For the actual function, it should create the plan while waiting for the user to navigate in the browser. It should also have a cool ui.
    except KeyboardInterrupt:
        if pw:
            pw.close()
        
        



if __name__ == "__main__":
    main()
