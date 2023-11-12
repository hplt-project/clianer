import curses


class MenuBar:
    def __init__(self, screen):
        self.screen = screen
        self.window = curses.newwin(1, curses.COLS, 0, 0)


    def render(self):
        self.window.bkgd(' ', curses.color_pair(6))
        self.window.addstr(0, 0, "File")
        self.window.addstr(0, 6, "Edit")
        self.window.addstr(0, 11, "View")
        self.window.addstr(0, 16, "Help")
        self.window.noutrefresh()
