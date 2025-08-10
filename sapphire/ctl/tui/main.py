import curses
from .curses_tui import SapphireTUI

def main(scr: curses.window):
    tui = SapphireTUI(scr)
    tui.run()

curses.wrapper(main)