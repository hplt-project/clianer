import json
import os
import urwid

FILTERS_LOCATION = "/home/helcl/hplt/OpusCleaner/opuscleaner/filters/"


def get_filters(location=FILTERS_LOCATION):
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


class AddFilterDialog(urwid.WidgetWrap):
    """Dialog overlay that lets user choose which filter to add"""

    def __init__(self, parent):
        self.available_filters = get_filters()

        self.buttons = []
        for name in self.available_filters.keys():
            self.buttons.append(urwid.Button(name, on_press=self.add_filter, user_data=name))

        self.listbox = urwid.ListBox(urwid.SimpleFocusListWalker(self.buttons))

        urwid.register_signal(self.__class__, ["close"])
        super().__init__(urwid.LineBox(self.listbox, title="New filter"))

    def add_filter(self, button, name):
        # just close and return focus to parent
        self._emit("close", name)
