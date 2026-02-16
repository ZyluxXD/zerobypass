#!/usr/bin/env python3
import asyncio
# Suppress Warning
import warnings

warnings.filterwarnings("ignore", category=UserWarning, module='stopit')
# ------------------------------------------------
from .helpers import wait_till_exit
from .algorithm import Algorithm
from .helpers import can_output_graphics, get_text, handle_disclaimer, wait_for_navigate
from .playwrighter import Playwrighter

# ------------------------------------------------
global pw


async def async_main(ctx):
    start = False
    while True:
        try:
            captured_text, _ = await get_text()
            if not start:
                await pw.start()
                start = True
            await wait_for_navigate()
            current_page = await ctx.get_current_page()
            algo = Algorithm(current_page)
            await algo.type_text(captured_text)
            await wait_till_exit()


        except asyncio.CancelledError:
            if ctx:
                await ctx.close()
            raise
        except Exception as e:
            # TODO: Better error logging
            if ctx:
                await ctx.close()
            raise e


def main():
    global pw
    try:
        can_output_graphics()
        handle_disclaimer()

        # TODO implement: implement rich text
        pw = Playwrighter()
        asyncio.run(async_main(pw))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
