import curses

SIDE_BAR_WIDTH = 40

class FilterListWindow:
    def __init__(self, screen):
        self.screen = screen
        self.filters = []
        self.selected_item = 0

        height = curses.LINES - 2
        width = SIDE_BAR_WIDTH
        self.window = curses.newwin(height, width, 1, 0)
        self.window.keypad(True)


    def render(self):
        self.window.border()

        for i in range(len(self.filters)):
            if i == self.selected_item:
                self.window.addstr(i + 2, 2, self.filters[i], curses.color_pair(1))
            else:
                self.window.addstr(i + 2, 2, self.filters[i])

        self.window.noutrefresh()

    def handle_input(self, key):
        if key == curses.KEY_UP:
            self.selected_item = max(0, self.selected_item - 1)
        elif key == curses.KEY_DOWN:
            self.selected_item = min(len(self.filters) - 1, self.selected_item + 1)

    def add_filter(self, filter_name):
        self.filters.append(filter_name)
