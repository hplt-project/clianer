import curses


class StatusBar:
    def __init__(self, screen):
        self.screen = screen
        self.message = "Ready."
        self.window = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)

    def set_message(self, message):
        self.message = message

    def reset_message(self, message):
        self.message = "Ready."

    def render(self):
        self.window.erase()
        self.window.bkgd(' ', curses.color_pair(3))
        self.window.addstr(0, 0, self.message)
        self.window.noutrefresh()
