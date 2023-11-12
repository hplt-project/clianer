import curses
from clianer.components.filter_list_window import SIDE_BAR_WIDTH

class MainWindow:
    def __init__(self, screen):
        self.screen = screen

        self.height = curses.LINES - 2
        self.width = curses.COLS - SIDE_BAR_WIDTH
        self.window = curses.newwin(self.height, self.width, 1, SIDE_BAR_WIDTH)
        self.window.keypad(True)
        self.dataset = None

    def render(self):
        # put message in the middle of the main window
        self.window.border()
        if self.dataset is None:
            #self.window.addstr(1, 1, "Main Window")
            message = "Press q to exit"
            self.window.addstr(self.height // 2, self.width // 2 - len(message) // 2, message)

        else:
            pass

        self.window.noutrefresh()
