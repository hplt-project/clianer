import curses
import json
import os

from clianer.components.main_window import MainWindow
from clianer.components.filter_list_window import FilterListWindow
from clianer.components.status_bar import StatusBar
from clianer.components.menu_bar import MenuBar
from clianer.components.choose_filter_dialog import ChooseFilterDialog
from clianer.components.choose_dataset_dialog import ChooseDatasetDialog


FILTERS_LOCATION = "/home/helcl/hplt/OpusCleaner/opuscleaner/filters/"
DATA_LOCATION = "/home/helcl/hplt/OpusCleaner/data/train-parts"

def get_filters(location):
    """Returns a list of filters from the given location and its subdirectories"""
    filters = {}

    for root, _, paths in os.walk(location):

        for path in paths:
            filename = os.path.join(root, path)
            if path.endswith(".json"):
                name = filename[len(location):].replace("/", ".").replace(".json", "")

                # parse the json
                with open(os.path.join(root, path), "r") as f:
                    filter_cfg = json.load(f)
                    filters[name] = filter_cfg

    return filters


def get_datasets(location):
    datasets = []

    for root, _, paths in os.walk(location):
        for path in paths:
            filename = os.path.join(root, path)
            name = filename[len(location):]

            datasets.append(filename)

    return datasets


class App:
    def __init__(self, screen):
        self.screen = screen

        self.filters = get_filters(FILTERS_LOCATION)
        self.datasets = get_datasets(DATA_LOCATION)
        self.main_window = MainWindow(screen)
        self.filter_list = FilterListWindow(screen)
        self.status_bar = StatusBar(screen)
        self.menu_bar = MenuBar(screen)

    def render(self):
        self.main_window.render()
        self.filter_list.render()
        self.status_bar.render()
        self.menu_bar.render()

        curses.doupdate()

    def handle_input(self, key):
        if key == ord("q") or key == ord("Q"):
            return False
        elif key == ord("n") or key == curses.KEY_F2:
            # open up add filter dialog
            dialog = ChooseFilterDialog(self.screen, list(self.filters.keys()))
            result = dialog.show()
            if result:
                self.status_bar.set_message("Filter added: " + result)
                self.filter_list.add_filter(result)
        elif key == ord("d") or key == curses.KEY_F3:
            dialog = ChooseDatasetDialog(self.screen, self.datasets[:20])
            result = dialog.show()
            if result:
                self.status_bar.set_message("Dataset added: " + result)
                pass
        else:
            self.filter_list.handle_input(key)

    def run(self):

        while True:
            self.screen.refresh()

            self.render()
            key = self.screen.getch()
            result = self.handle_input(key)

            if result is False:
                break
