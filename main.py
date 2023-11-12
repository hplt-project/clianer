#!/usr/bin/env python3

import curses
from clianer.app import App


def main(stdscr):
    # Clear screen
    stdscr.clear()

    # initilaize color pairs
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

    # create windows
    App(stdscr).run()


if __name__ == "__main__":
    curses.wrapper(main)
