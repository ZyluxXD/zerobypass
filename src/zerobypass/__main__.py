#!/usr/bin/env python3
# Suppress Warning
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module='stopit')
# ------------------------------------------------
from .config import args
from .helpers import wait_till_exit
from .algorithm import Algorithm
from .helpers import can_output_graphics, get_text, handle_disclaimer, wait_for_navigate
from .playwrighter import Playwrighter
# ------------------------------------------------
global pw
def main():
    if args.verbose:
        pass
        # TODO add: I dont really wanna do it right now so ill do it later
    global pw
    try:
        pw = None
        can_output_graphics()
        handle_disclaimer()
        captured_text, _ = get_text()
        pw = Playwrighter()
        wait_for_navigate()
        Algorithm(pw.current_page).type_text(captured_text)
        wait_till_exit()
    except KeyboardInterrupt:
        if pw:
            pw.close()
        
        



if __name__ == "__main__":
    main()
