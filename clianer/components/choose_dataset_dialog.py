import curses

class ChooseDatasetDialog:
    def __init__(self, screen, datasets):
        self.screen = screen
        self.datasets = datasets

        height = len(self.datasets) + 4
        width = max(len(f) for f in self.datasets) + 4
        y = (curses.LINES - height) // 2
        x = (curses.COLS - width) // 2
        self.window = curses.newwin(height, width, y, x)
        self.window.keypad(True)
        self.selected_item = 0


    def render(self):
        self.window.border()

        y_offset = 2
        x_offset = 2

        for i in range(len(self.datasets)):
            if i == self.selected_item:
                self.window.addstr(i + y_offset, x_offset, self.datasets[i], curses.color_pair(1))
            else:
                self.window.addstr(i + y_offset, x_offset, self.datasets[i])

        self.window.noutrefresh()

    def handle_input(self, key):
        if key == curses.KEY_UP:
            self.selected_item = max(0, self.selected_item - 1)
        elif key == curses.KEY_DOWN:
            self.selected_item = min(len(self.datasets) - 1, self.selected_item + 1)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            self.close()
            return self.datasets[self.selected_item]
        elif key == ord('q') or key == ord('Q'):
            self.close()
            return False


    def close(self):
        self.window.clear()
        self.window.noutrefresh()
        del self.window

    def show(self):
        self.render()
        self.window.refresh()

        while True:
            key = self.window.getch()
            result = self.handle_input(key)

            if result is not None:
                return result

            self.render()
            self.window.refresh()
