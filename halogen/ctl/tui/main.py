import curses
from .curses_tui import HalogenTUI

def main(scr: curses.window):
    tui = HalogenTUI(scr)
    tui.run()

curses.wrapper(main)